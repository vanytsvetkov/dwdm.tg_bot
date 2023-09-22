# dwdm.tg_bot

## Dependencies
```shell
python 3.11.2
redis 6.0.16
kafka 0.7.1
```

## Deployment

#### 0. Setup venv and install requirements
```shell
$ python3 -m venv venv
$ source venv/bin/activate
$ python3 -m pip install -r requirements.txt
```
Be careful, if you call your virtual environment by a different name, you will need to modify the `build.sh` script.

#### 1. Build scripts' basement
```shell
$ chmod +x build.sh
$ ./build.sh
```

#### 2. Add new rules to crontab
```shell
$ cat scripts/cron.sh 
$ crontab -e
```

#### 3. Add data to local storages
```shell
$ vim data/credentials.json 
$ vim data/api-project.json
$ vim vars.py
```

#### 4. Running
```shell
$  ln -s dwdm.tg_bot.send.service /etc/systemd/system/dwdm.tg_bot.send.service
$  ln -s dwdm.tg_bot.listen.service /etc/systemd/system/dwdm.tg_bot.listen.service

$  systemctl enable dwdm.tg_bot.listen.service
$  systemctl start dwdm.tg_bot.listen.service 

$  systemctl enable dwdm.tg_bot.send.service
$  systemctl start dwdm.tg_bot.send.service
```

## Scripts

This system consists of four Python scripts designed for data synchronization, comparison, and patching tasks. Each script serves a unique purpose but contributes to a comprehensive data management workflow.

### 1. Comparator Script

- **Purpose:** Compares data between reference and probe datasets.
- **Key Features:**
  - Fetches data from Google Tables and an MCP server.
  - Compares data based on specific columns.
  - Generates styled comparison reports.
  - Sends reports to recipients via Telegram.

### 2. Redis Upload Script

- **Purpose:** Uploads data from an MCP server to a Redis database.
- **Key Features:**
  - Connects to a Redis database using configurable credentials.
  - Retrieves data about Ciena 6500 and Ciena WS devices from the MCP server.
  - Uploads device information to Redis with expiration settings.

### 3. Data Comparison and Patching Script

- **Purpose:** Compares and patches client data between Google Tables and the MCP server.
- **Key Features:**
  - Fetches client data from Google Tables and the MCP server.
  - Compares data to identify discrepancies.
  - Patches discrepancies in client data when found.
  - Sends reports and notifications via Telegram.

### 4. Data Cleanup Script

- **Purpose:** Performs data cleanup tasks on client data.
- **Key Features:**
  - Fetches client data from Google Tables and the MCP server.
  - Identifies and handles data inconsistencies.
  - Cleans up empty or incorrect client entries.
  - Generates reports on cleanup activities.

## Usage

To utilize the functionality of these scripts, ensure that the required dependencies and configurations are correctly set up for each script. You can execute each script using Python.

Refer to the individual README files for each script for detailed instructions on setup and usage.
