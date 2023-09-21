# Comparator Script

## Purpose

The `main.py` is designed to compare data from a reference dataset with data from a remote MCP (Multiple Customer Provisioning) server. It generates styled comparison tables and has the ability to send these results via Telegram.

## Dependencies

Ensure the following Python libraries and modules are installed:

- `asyncio`
- `logging`
- `os.path`
- `sys`
- `dataframe_image`
- `pandas`
- `requests.exceptions`

Additionally, make sure to have custom modules and dependencies like `interactors.McpAPI`, `utils.Senders`, `utils.utils`, and `vars` available.

To convert a pandas DataFrame to a png image using the Google driver (used by default), you need to install chromium on your system.

## Configuration

Key configuration variables:

- `CURRENT_DIR`: Script directory.
- `REPORT_DIR`: Directory for generated comparison reports (PNG images).
- `SHEET_NAME`: Reference dataset sheet name.
- `VALID_PREFIXES`: List of valid prefixes for data filtering.

## Comparison Logic

1. Fetch data from a Google Tables sheet (reference dataset).
2. Interact with MCP server to obtain probe data.
3. Compare data based on columns like wave name, resilience level, and customer.
4. Generate styled tables highlighting differences.
5. Save comparison tables in `REPORT_DIR`.

## Telegram Integration

The script can send results to Telegram recipients:
- Single recipient mode.
- Multiple recipients mode: Define recipients in configuration.

## How to Run

Execute the script using Python. Ensure dependencies and configurations are set up:

```shell
$ python3 main.py [chat_id] [msg_id]
```