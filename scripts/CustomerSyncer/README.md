# Syncer Script

## Purpose

The `main.py` is designed to perform a comparison of client data between a Google Tables dataset and a remote MCP (Multiple Customer Provisioning) server dataset. It identifies differences and, if necessary, patches discrepancies in the client data.

## Dependencies

Ensure the following Python libraries and modules are installed:

- `asyncio`
- `logging`
- `sys`
- `vars`
- Custom modules: `interactors.McpAPI`, `utils.Senders`, `utils.utils`

## Configuration

Configuration settings are required for the script to run correctly. These settings include specifying sheet names, column names, and prefixes. Ensure that the necessary configurations are correctly set up in the `vars` module.

## Data Comparison and Patching Logic

1. Initialize logging and load credentials.
2. Determine whether the script should send reports to a single recipient or multiple recipients via Telegram.
3. Fetch data from Google Tables for specified sheet names.
4. Extract client data and relevant columns from the Google Tables dataset.
5. Fetch data from the MCP server using the MCP API.
6. Extract client data from the MCP dataset.
7. Compare client data from Google Tables with client data from the MCP server.
8. If discrepancies are found:
   - Patch the MCP dataset with the correct client data.
   - Keep track of the number of patches made.
9. Identify empty customer entries in the Google dataset and send a notification if found.
10. Generate and send a report with the results of the comparison and any patches made.

## How to Run

Execute the script using Python. Ensure that the required dependencies and configurations are correctly set up:

```shell
$ python3 data_comparison_patching_script.py [chat_id] [msg_id]
```
