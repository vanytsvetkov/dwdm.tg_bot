# dwdm.tg_bot

### Deploy

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
$ python3 main.py > /dev/null 2>&1 &
$ python3 bot.py > /dev/null 2>&1 &
```

### If you need to make some changes:

#### 1. To change cron rules
```shell
$ vim build.sh
$ ./build.sh
$ cat scripts/cron.sh
$ crontab -e
```
