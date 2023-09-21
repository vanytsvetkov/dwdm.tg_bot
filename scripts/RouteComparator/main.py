import asyncio
import logging as log
import os.path
import sys

import dataframe_image as dfi
import pandas as pd
from requests.exceptions import RequestException

import vars
from interactors.McpAPI import McpAPI
from utils.Senders import send_tg_msg
from utils.utils import get_df_from_gt, is_valid, load_creds

CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))
REPORT_DIR = f'{CURRENT_DIR}/result'
REPORT_FN = lambda x: f'{REPORT_DIR}/comparator_result_{x + 1}.png'

SHEET_NAME = 'ROUTES'

COL_WAVE_NAME = 0
COL_WAVE_RESILIENSE = 1
COL_WAVE_CLIENT = 2
COL_WAVE_NODES = 3

VALID_PREFIXES = ["G-", "GBL-", "RUN-", "TG-", "TG-SGP-"]


def colorise(line: pd.Series) -> list[str]:
    global COL_WAVE_NAME, COL_WAVE_RESILIENSE, COL_WAVE_CLIENT, COL_WAVE_NODES
    global reference_nodes, reference_resilienceLevels, reference_customers
    global probe_nodes, probe_resilienceLevels, probe_customers

    STYLE_SUCCESS_BG = 'background-color: #c1d08a;'
    STYLE_SUCCESS_TC = 'color: #000000;'
    STYLE_FAILED_BG = 'background-color: #fcd1d6;'
    STYLE_FAILED_MISS_BG = 'background-color: #f79ca6;'
    STYLE_FAILED_TC = 'color: #dc4a68;'
    STYLE_BORDER = 'border: 1px solid grey;'

    STYLE_BOLD = 'font-weight: bold;'
    STYLE_BG = lambda x: 'background-color: #f5f5f5;' if x % 2 else 'background-color: #ffffff;'

    STYLE_SUCCESS = f'{STYLE_SUCCESS_BG} {STYLE_BORDER}'
    STYLE_FAILED = f'{STYLE_FAILED_BG} {STYLE_BORDER}'
    STYLE_FAILED_MISS = f'{STYLE_FAILED_MISS_BG} {STYLE_BORDER}'

    waveName = line[COL_WAVE_NAME]
    if waveName in probe_nodes:
        BaseSchema = [''] * len(line)

        BaseSchema[COL_WAVE_NAME] = f'{STYLE_BOLD} {STYLE_BORDER} {STYLE_BG(line.name)}'
        BaseSchema[COL_WAVE_RESILIENSE] = STYLE_SUCCESS if reference_resilienceLevels[waveName] == probe_resilienceLevels[waveName] else STYLE_FAILED
        if reference_customers.get(waveName, None):
            BaseSchema[COL_WAVE_CLIENT] = f'{STYLE_SUCCESS_TC} {STYLE_BG(line.name)}' if reference_customers[waveName] == probe_customers[waveName] else f'{STYLE_FAILED_TC} {STYLE_BG(line.name)}'

        if reference_nodes[waveName].issubset(probe_nodes[waveName]):
            BaseSchema[COL_WAVE_NODES:] = [STYLE_SUCCESS] * len(BaseSchema[COL_WAVE_NODES:])
        else:
            for node_id, nodeName in enumerate(line[COL_WAVE_NODES:]):
                BaseSchema[COL_WAVE_NODES+node_id] = STYLE_FAILED if nodeName in probe_nodes[waveName] or nodeName == '' else STYLE_FAILED_MISS

        return BaseSchema
    else:
        return [STYLE_BOLD] * len(line)


if __name__ == '__main__':
    log.basicConfig(level=log.DEBUG)

    os.makedirs(REPORT_DIR, exist_ok=True)

    creds = load_creds()

    REPORT_RECIPIENT = None
    REPORT_RECIPIENTS = None

    if len(sys.argv) > 2:
        REPORT_RECIPIENT = {
            'chat_id': int(sys.argv[1]),
            'msg_id': int(sys.argv[2])
            }
    else:
        REPORT_RECIPIENTS = {
            *creds.tg[vars.BOT_NAME].users.values(),
            *creds.tg[vars.BOT_NAME].groups.values(),
            }

    # Get reference dataset from Google Tables
    try:
        df = get_df_from_gt(sheet_id=creds.gtable.sheet_id, sheet_names=[SHEET_NAME])

        dataset = df[SHEET_NAME]
    except Exception:
        text = 'Failed to get dataset from Google Tables.'
        log.critical(text)
        if REPORT_RECIPIENT:
            asyncio.run(send_tg_msg(text=text, chat_id=REPORT_RECIPIENT['chat_id'], reply_to_message_id=REPORT_RECIPIENT['msg_id'], token=creds.tg[vars.BOT_NAME].token))
        raise

    reference_nodes = {}
    reference_resilienceLevels = {}
    reference_customers = {}

    # Get probes dataset from MCP
    try:
        mcp = McpAPI(creds)

        probe_nodes = {}
        probe_resilienceLevels = {}
        probe_customers = {}

        for _, row in dataset.iterrows():
            wave = row.iloc[COL_WAVE_NAME]
            if is_valid(wave, VALID_PREFIXES):
                nodes = row.iloc[COL_WAVE_NODES:]
                reference_nodes.setdefault(wave, set(node for node in nodes if node))

                resilienceLevel = row.iloc[COL_WAVE_RESILIENSE]
                reference_resilienceLevels.setdefault(wave, resilienceLevel)

                customer = row.iloc[COL_WAVE_CLIENT]
                reference_customers.setdefault(wave, customer)

                try:
                    get = mcp.get_fres(displayName=wave, serviceClass=['Photonic'])
                except RequestException:
                    log.critical(f'Failed to receive a response from the remote MCP server: {creds.mcp.url}')
                    raise

                if get.success:
                    for fre in get.response.data:
                        serviceTopology = mcp.get_serviceTopology(id_=fre.id)
                        if serviceTopology.success:
                            nodes = {neName for node in serviceTopology.response.included if (neName := node.attributes.locations[0].neName)}

                            probe_nodes.setdefault(wave, nodes)
                            probe_resilienceLevels.setdefault(wave, serviceTopology.response.data.attributes.resilienceLevel)
                            probe_customers.setdefault(wave, serviceTopology.response.data.attributes.customerName)
                        break
    except Exception:
        text = 'Failed to get dataset from MCP.'
        log.critical(text)
        if REPORT_RECIPIENT:
            asyncio.run(send_tg_msg(text=text, chat_id=REPORT_RECIPIENT['chat_id'], reply_to_message_id=REPORT_RECIPIENT['msg_id'], token=creds.tg[vars.BOT_NAME].token))
        raise

    # Set table plots rules
    pd.set_option("display.max_column", None)
    pd.set_option("display.max_colwidth", None)
    pd.set_option('display.width', -1)
    pd.set_option('display.max_rows', None)

    # Split reference dataset by customer types
    prev_splitIndex = 0
    splitIndexes = list(dataset.index[dataset.iloc[:, COL_WAVE_NODES].isna()][1:]) + [-1]
    for i, splitIndex in enumerate(splitIndexes):
        dataset_i = dataset[prev_splitIndex:splitIndex] if splitIndex != -1 else dataset[prev_splitIndex:]
        prev_splitIndex = splitIndex

        dataset_i = dataset_i.dropna(axis=1, how='all').fillna('')

        # Apply colorise function and export to a file
        dataset_i_styled = dataset_i.style.apply(colorise, axis=1)

        # Hiding rows and columns indexes
        dataset_i_styled.hide().hide(axis='columns')

        dfi.export(dataset_i_styled, REPORT_FN(i))

        # Send result to telegram
        if REPORT_RECIPIENT is None:
            for recipient in REPORT_RECIPIENTS:
                asyncio.run(send_tg_msg(filename=REPORT_FN(i), chat_id=recipient, token=creds.tg[vars.BOT_NAME].token))
        else:
            asyncio.run(send_tg_msg(filename=REPORT_FN(i), chat_id=REPORT_RECIPIENT['chat_id'], reply_to_message_id=REPORT_RECIPIENT['msg_id'], token=creds.tg[vars.BOT_NAME].token))
