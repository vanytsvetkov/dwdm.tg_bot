import asyncio
import logging as log
import sys

import vars
from interactors.McpAPI import McpAPI
from utils.Senders import send_tg_msg
from utils.utils import get_df_from_gt, is_ignore, is_valid, load_creds, prettify

SHEET_NAMES = ["DWDM", "Telegram AMS"]
COL_CHANNEL_NAME = 0
COL_NAME_IGNORE = 'Ignore'
SEARCH_LIMIT = 10000
REPORT_REF_FN = 'channels_not_in_gt.txt'
REPORT_PROBE_FN = 'channels_not_in_mcp.txt'
REPORT_SUCCESSFUL_TXT = 'In the MCP and GTables databases, identical channels are stored.\nCongratulations!'

VALID_PREFIXES = ["G-", "GBL-", "RUN-", "TG-", "TG-SGP-"]

if __name__ == '__main__':
    log.basicConfig(level=log.DEBUG)

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

    mcp = McpAPI(creds)

    # Get reference dataset from Google Tables

    try:
        df = get_df_from_gt(sheet_id=creds.gtable.sheet_id, sheet_names=SHEET_NAMES)

        reference_channels = set()
        for sheet in SHEET_NAMES:
            dataset = df[sheet][1:]
            dataset.columns = df[sheet].iloc[0]

            col_ignore = dataset.columns.get_loc(COL_NAME_IGNORE) if COL_NAME_IGNORE in dataset.columns else None

            for _, row in dataset.iterrows():
                if not is_ignore(row, col_ignore):
                    channelName = row.iloc[COL_CHANNEL_NAME]
                    if is_valid(channelName, VALID_PREFIXES):
                        reference_channels.add(channelName)
    except Exception:
        text = 'Failed to get dataset from Google Tables.'
        log.critical(text)
        if REPORT_RECIPIENT:
            asyncio.run(send_tg_msg(text=text, chat_id=REPORT_RECIPIENT['chat_id'], reply_to_message_id=REPORT_RECIPIENT['msg_id'], token=creds.tg[vars.BOT_NAME].token))
        raise

    # Get probe dataset from MCP

    try:
        probe_channels = set()

        get = mcp.get_fres(serviceClass=['Transport Client'], limit=SEARCH_LIMIT)
        if get.success:
            for fre in get.response.data:
                channelName = fre.attributes.displayData.displayName
                if is_valid(channelName, VALID_PREFIXES):
                    probe_channels.add(prettify(channelName))
    except Exception:
        text = 'Failed to get dataset from MCP.'
        log.critical(text)
        if REPORT_RECIPIENT:
            asyncio.run(send_tg_msg(text=text, chat_id=REPORT_RECIPIENT['chat_id'], reply_to_message_id=REPORT_RECIPIENT['msg_id'], token=creds.tg[vars.BOT_NAME].token))
        raise

    # Comparing

    nonexistent_probe_channels = reference_channels - probe_channels
    nonexistent_ref_channels = probe_channels - reference_channels

    # Send report to TG

    if nonexistent_ref_channels:
        data = {'data': '\n'.join(nonexistent_ref_channels), 'filename': REPORT_REF_FN}
        if REPORT_RECIPIENT is None:
            for recipient in REPORT_RECIPIENTS:
                asyncio.run(send_tg_msg(data=data, chat_id=recipient, token=creds.tg[vars.BOT_NAME].token))
        else:
            asyncio.run(send_tg_msg(data=data, chat_id=REPORT_RECIPIENT['chat_id'], reply_to_message_id=REPORT_RECIPIENT['msg_id'], token=creds.tg[vars.BOT_NAME].token))

    if nonexistent_probe_channels:
        data = {'data': '\n'.join(nonexistent_probe_channels), 'filename': REPORT_PROBE_FN}
        if REPORT_RECIPIENT is None:
            for recipient in REPORT_RECIPIENTS:
                asyncio.run(send_tg_msg(data=data, chat_id=recipient, token=creds.tg[vars.BOT_NAME].token))
        else:
            asyncio.run(send_tg_msg(data=data, chat_id=REPORT_RECIPIENT['chat_id'], reply_to_message_id=REPORT_RECIPIENT['msg_id'], token=creds.tg[vars.BOT_NAME].token))

    if not nonexistent_ref_channels and not nonexistent_probe_channels:
        if REPORT_RECIPIENT is None:
            for recipient in REPORT_RECIPIENTS:
                asyncio.run(send_tg_msg(text=REPORT_SUCCESSFUL_TXT, chat_id=recipient, token=creds.tg[vars.BOT_NAME].token))
        else:
            asyncio.run(send_tg_msg(text=REPORT_SUCCESSFUL_TXT, chat_id=REPORT_RECIPIENT['chat_id'], reply_to_message_id=REPORT_RECIPIENT['msg_id'], token=creds.tg[vars.BOT_NAME].token))
