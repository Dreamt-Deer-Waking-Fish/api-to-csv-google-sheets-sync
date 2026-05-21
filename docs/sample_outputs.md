# Sample Outputs

This repository includes a generated CSV export so a client can inspect the result without running the workflow first.

## Preview

![Sample output preview](../screenshots/sample_output_preview.png)

## Included Files

| File | Purpose |
| --- | --- |
| [`output/api_data.csv`](../output/api_data.csv) | Normalized spreadsheet-ready product data from the public API |
| [`sample_data/api_products.json`](../sample_data/api_products.json) | Local JSON fixture for offline validation and CI |

## Review Notes

The default output uses public Fake Store API data and does not require credentials. The local JSON fixture exists so CI and client demos can run without depending on external API availability. Client-specific API exports should be reviewed for private or sensitive fields before publishing.
