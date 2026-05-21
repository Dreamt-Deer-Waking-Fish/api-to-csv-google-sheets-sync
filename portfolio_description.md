# Upwork Case Study: API Data Export to CSV and Google Sheets

## Portfolio Title

I built a Python API integration that converts JSON data into a clean CSV and optional Google Sheet.

## Client Scenario

A business needs product, inventory, CRM, or vendor data from an API, but the raw JSON response is difficult for the operations team to review. They need a spreadsheet-ready export that can be opened in Excel, uploaded to another tool, or synced to Google Sheets.

## My Solution

I created a Python workflow that requests data from an API endpoint, flattens nested JSON fields, standardizes the columns, exports a CSV, and optionally syncs the same data into Google Sheets using a service account.

## Key Deliverables

- Configurable API endpoint
- JSON-to-table normalization
- Clean CSV export
- Optional Google Sheets sync
- Safe `.env.example` credential setup
- Error handling and logging
- README with setup, usage, and client adaptation notes

## Business Result

This workflow removes manual copy/paste work and creates a repeatable bridge between APIs and spreadsheet-based business operations.

## Technologies Used

Python, requests, pandas, python-dotenv, gspread, Google service-account workflow.

## How I Would Customize It for a Client

For a real project, I would add the client's API authentication, pagination, field mapping, scheduled execution, and destination-specific formatting.
