import html
import json
import logging as log
import os
import re
import sys

import gspread
import pandas as pd
import redis as r

import vars
from models.Creds import Creds


def load_creds() -> Creds:

    if not all(os.path.exists(os.path.join(vars.BASE, vars.DATA_DIR, file)) for file in vars.NECESSARY_FILES):
        log.critical(f'Please ensure that all required files are located in the "{vars.DATA_DIR}" directory.')
        sys.exit(0)

    with open(os.path.join(vars.BASE, vars.DATA_DIR, vars.CREDITS_FILENAME)) as credits_file:
        credits = Creds.model_validate(json.load(credits_file))

    return credits


def get_df_from_gt(sheet_id: str, sheet_names: list) -> dict[str, pd.DataFrame]:
    """
    man: https://medium.com/geekculture/2-easy-ways-to-read-google-sheets-data-using-python-9e7ef366c775#c6bb
    :param sheet_id:
    :param sheet_names:
    :return: DataFrame
    """
    GoogleClient = gspread.service_account(os.path.join(vars.BASE, vars.DATA_DIR, vars.GOOGLE_API_FILENAME))
    spreadsheet = GoogleClient.open_by_key(sheet_id)
    dataframes = []
    for sheet_name in sheet_names:
        worksheet = spreadsheet.worksheet(sheet_name)
        df = pd.DataFrame(worksheet.get())
        dataframes.append(df)

    return dict(zip(sheet_names, dataframes))


def is_valid(name: str, validators: list) -> bool:
    return any(name.startswith(prefix) for prefix in validators)


def is_ignore(line: pd.Series, index: int | None = None) -> bool:
    return index is not None and line.iloc[index]


def prettify(name: str) -> str:
    # found = re.findall(r'([\w+-]+\d+).*', name)
    # return found[0] if found else None
    found = re.match(r'([\w+-]+\d+)', name)
    return found.group(1) if found else None


def unformat_custom_sub(match):
    match (word := match.group(1)):
        case 'RESOURCE' | 'RESO' | 'URCE':
            return fr'(?P<_{word}>[-\/.A-Za-z0-9_]*)'
        case 'MSG':
            return fr'(?P<_{word}>.+:*?)'
        case _:
            return fr'(?P<_{word}>.+)'


def unformat(string: str, pattern: str, i: int = 0) -> dict:
    _pattern = re.sub(r'</?var\d*>', '', pattern)
    regexp_pattern = re.sub(r'{(.+?)}', unformat_custom_sub, _pattern)
    search = re.search(regexp_pattern, string)
    if search:
        values = list(search.groups())
        keys = re.findall(r"{(.+?)}", _pattern)
        _dict = dict(zip(keys, values))
        return _dict | {'processed': bool(_dict), 'regexp_pattern': regexp_pattern}
    elif not search and re.search(r'</?var\d*>', pattern):
        new_pattern = re.sub(fr"<var{i if i else ''}>.+?</var{i if i else ''}>", "", pattern)
        return unformat(string, new_pattern, i+1)
    else:
        return {'processed': False , 'regexp_pattern': regexp_pattern}


def is_logType(cond, text: str) -> bool:
    match = re.search(fr'\W({cond})\W', text)
    return bool(match)


def get_log_level(text: str) -> str:
    match = re.search(r'\b(?:ALM|SECU|DBCHG)\b', text)
    return match.group() if match else str()


def get_event_id(text: str) -> str:
    match = re.search(r'EVENT-ID[=:]"?(\d+-\d+)"?', text)
    return match.group(1) if match else str()


def get_event_name(text: str) -> str:
    match = re.search(r'EVENT-NAME[=:]"?(\w+)"?', text)
    return match.group(1) if match else str()


def get_log_prival(text: str) -> str:
    match = re.search(r'<(\d+)>', text)
    return match.group(1) if match else str()


def get_affected_services(device: str, tpe: str, redis: r.Redis) -> str:
    fres = redis.smembers(f'{vars.PROJECT_NAME}.mcp.devices.{device}.tpes.{tpe}.fres')
    if fres:
        services = ', '.join(f'<code>{html.escape(fre)}</code>' for fre in sorted(fres))
        return services

    return str()
