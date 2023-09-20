import gspread
import json
import sys
import vars
import os
import pandas as pd
import logging as log
from models.Creds import Creds


def load_creds() -> Creds:

    if not all(os.path.exists(os.path.join(vars.BASE, vars.DATA_DIR, file)) for file in vars.NECESSARY_FILES):
        log.critical(f'Please ensure that all required files are located in the "{vars.DATA_DIR}" directory.')
        sys.exit(0)

    with open(os.path.join(vars.BASE, vars.DATA_DIR, vars.CREDITS_FILENAME)) as credits_file:
        credits = Creds.model_validate(json.load(credits_file))

    return credits


def escape_html_tags(text: str) -> str:
    return text.replace('<', '&lt;').replace('>', '&gt;')


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
