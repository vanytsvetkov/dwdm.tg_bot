# README for Redis Upload Script

## Purpose

The `main.py` script is responsible for uploading data from the MCP (Multiple Customer Provisioning) server to a Redis database. It specifically uploads information related to Ciena 6500 and Ciena WS devices.

## Dependencies

Ensure the following Python libraries and modules are installed:

- `datetime.timedelta`
- `vars`
- `redis`
- `logging`
- Custom modules: `interactors.McpAPI`, `utils.utils`

## Configuration

The script relies on configuration settings provided in the `vars` module. Ensure that the necessary configurations are correctly set up there.

## Redis Upload Logic

1. Initialize logging and load credentials.
2. Connect to the Redis database using credentials from the loaded configuration.
3. Use the MCP API to fetch data about Ciena 6500 devices.
4. For each Ciena 6500 device and its associated shelves:
   - Upload display name, type group, and resource type to Redis.
   - Set an expiration time for the Redis keys (7 days).
5. Use the MCP API to fetch data about Ciena WS devices.
6. For each Ciena WS device:
   - Upload display name, type group, and resource type to Redis.
   - Set an expiration time for the Redis keys (7 days).
7. Close the Redis connection.

## How to Run

Simply execute the script using Python. Ensure that the required dependencies and configurations are correctly set up:

```shell
python3 main.py
```