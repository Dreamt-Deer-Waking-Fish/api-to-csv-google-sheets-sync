# Client Delivery Notes

## What the Client Receives

- A reusable Python API export script
- CSV output suitable for Excel, Google Sheets, or downstream imports
- Optional Google Sheets sync workflow
- Safe credential setup instructions
- Documentation for endpoint customization

## Acceptance Checklist

- `python -m py_compile main.py` passes
- `python main.py` exports `output/api_data.csv`
- CSV contains normalized product-style columns
- Runtime logs are generated locally and excluded from Git
- Optional Google Sheets sync is documented without committing credentials

## Client Customization Options

- Add API authentication headers
- Add pagination
- Add custom field mapping
- Add scheduled runs
- Add Google Drive folder organization
- Add notifications after successful sync
