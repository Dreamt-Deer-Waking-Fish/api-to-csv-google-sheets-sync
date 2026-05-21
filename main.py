from __future__ import annotations

import argparse
import json
import logging
import os
from pathlib import Path
from typing import Any, Dict, List, Optional

import pandas as pd
import requests
from dotenv import load_dotenv


DEFAULT_ENDPOINT = "https://fakestoreapi.com/products"


def configure_logging(output_dir: Path) -> None:
    output_dir.mkdir(parents=True, exist_ok=True)
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s | %(levelname)s | %(message)s",
        handlers=[
            logging.StreamHandler(),
            logging.FileHandler(output_dir / "run.log", mode="w", encoding="utf-8"),
        ],
    )


def fetch_api_data(endpoint: str, timeout: int, use_system_proxy: bool) -> List[Dict[str, Any]]:
    logging.info("Fetching data from %s", endpoint)
    session = requests.Session()
    session.trust_env = use_system_proxy
    response = session.get(endpoint, timeout=timeout)
    response.raise_for_status()
    data = response.json()
    if isinstance(data, dict):
        for value in data.values():
            if isinstance(value, list):
                return value
        return [data]
    if isinstance(data, list):
        return data
    raise ValueError("API response must be a JSON object or array")


def load_json_data(input_json: Path) -> List[Dict[str, Any]]:
    if not input_json.exists():
        raise FileNotFoundError(f"JSON input file not found: {input_json}")
    logging.info("Loading API records from local JSON file %s", input_json)
    with input_json.open("r", encoding="utf-8") as file:
        data = json.load(file)
    if isinstance(data, dict):
        for value in data.values():
            if isinstance(value, list):
                return value
        return [data]
    if isinstance(data, list):
        return data
    raise ValueError("JSON input must be an object or array")


def normalize_products(records: List[Dict[str, Any]]) -> pd.DataFrame:
    if not records:
        raise ValueError("API returned no records")

    table = pd.json_normalize(records)
    column_map = {
        "id": "product_id",
        "title": "product_title",
        "price": "price",
        "description": "description",
        "category": "category",
        "image": "image_url",
        "rating.rate": "rating",
        "rating.count": "rating_count",
    }
    available_columns = [column for column in column_map if column in table.columns]
    clean = table[available_columns].rename(columns=column_map)

    for column in ["product_id", "product_title", "price", "description", "category", "image_url", "rating", "rating_count"]:
        if column not in clean.columns:
            clean[column] = pd.NA

    clean["price"] = pd.to_numeric(clean["price"], errors="coerce").fillna(0)
    clean["rating"] = pd.to_numeric(clean["rating"], errors="coerce")
    clean["rating_count"] = pd.to_numeric(clean["rating_count"], errors="coerce").fillna(0).astype(int)
    clean["product_title"] = clean["product_title"].astype(str).str.strip()
    clean["category"] = clean["category"].astype(str).str.strip()
    clean["description"] = clean["description"].astype(str).str.replace(r"\s+", " ", regex=True).str.strip()
    clean = clean.sort_values(["category", "product_title"]).reset_index(drop=True)
    return clean[
        [
            "product_id",
            "product_title",
            "category",
            "price",
            "rating",
            "rating_count",
            "description",
            "image_url",
        ]
    ]


def export_csv(data: pd.DataFrame, output_path: Path) -> Path:
    output_path.parent.mkdir(parents=True, exist_ok=True)
    data.to_csv(output_path, index=False, encoding="utf-8")
    logging.info("CSV exported to %s", output_path)
    return output_path


def sync_to_google_sheets(data: pd.DataFrame, sheet_name: str) -> None:
    credentials_path = os.getenv("GOOGLE_APPLICATION_CREDENTIALS")
    if not credentials_path:
        raise ValueError("GOOGLE_APPLICATION_CREDENTIALS is not set")

    try:
        import gspread
    except ImportError as exc:
        raise ImportError("Install optional dependency with: pip install gspread") from exc

    client = gspread.service_account(filename=credentials_path)
    spreadsheet = client.open(sheet_name)
    worksheet = spreadsheet.sheet1
    worksheet.clear()
    worksheet.update([data.columns.tolist()] + data.astype(str).values.tolist())
    logging.info("Synced %s rows to Google Sheet '%s'", len(data), sheet_name)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Fetch public API data, normalize JSON, and export a clean CSV.")
    parser.add_argument("--endpoint", default=DEFAULT_ENDPOINT, help="Public JSON API endpoint.")
    parser.add_argument("--input-json", default="", help="Optional local JSON file for offline validation or demos.")
    parser.add_argument("--output", default="output/api_data.csv", help="CSV output path.")
    parser.add_argument("--timeout", type=int, default=20, help="API request timeout in seconds.")
    parser.add_argument("--use-system-proxy", action="store_true", help="Use proxy settings from the local environment.")
    parser.add_argument("--sync-google-sheets", action="store_true", help="Optionally sync the CSV data to Google Sheets.")
    parser.add_argument("--sheet-name", default="", help="Google Sheet name, required when syncing.")
    return parser.parse_args()


def main() -> None:
    load_dotenv()
    args = parse_args()
    output_path = Path(args.output)
    configure_logging(output_path.parent)

    try:
        records = load_json_data(Path(args.input_json)) if args.input_json else fetch_api_data(args.endpoint, args.timeout, args.use_system_proxy)
        clean_data = normalize_products(records)
        export_csv(clean_data, output_path)
        if args.sync_google_sheets:
            if not args.sheet_name:
                raise ValueError("--sheet-name is required with --sync-google-sheets")
            sync_to_google_sheets(clean_data, args.sheet_name)
        logging.info("Done. Exported %s API records.", len(clean_data))
    except Exception as exc:
        logging.exception("API sync failed: %s", exc)
        raise SystemExit(1)


if __name__ == "__main__":
    main()
