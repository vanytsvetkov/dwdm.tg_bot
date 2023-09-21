import asyncio
import logging as log
import sys

import vars
from interactors.McpAPI import McpAPI
from utils.Senders import send_tg_msg
from utils.utils import get_df_from_gt, is_ignore, is_valid, load_creds, prettify

SHEET_NAMES = ["DWDM", "Telegram AMS"]
COL_CHANNEL_NAME = 0
COL_CHANNEL_CUSTOMER = 'Заказчик'
COL_CHANNEL_IGNORE = 'Ignore'
SEARCH_LIMIT = 10000

REPORT_SUCCESSFUL_TXT = 'The MCP and Google Tables databases store the same clients. Congratulations!'
REPORT_UNSUCCESSFUL_TXT = lambda x: f'Various clients were stored in the MCP and Google Tables databases. Fixed {x} client names.'

VALID_PREFIXES = ["G-", "GBL-", "RUN-", "TG-", "TG-SGP-"]

if __name__ == '__main__':
    log.basicConfig(level=vars.LOG_LEVEL)

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
        df = get_df_from_gt(sheet_id=creds.gtable.sheet_id, sheet_names=SHEET_NAMES)

        reference_customers = dict()
        for sheet in SHEET_NAMES:
            dataset = df[sheet][1:]
            dataset.columns = df[sheet].iloc[0]

            col_ignore = dataset.columns.get_loc(COL_CHANNEL_IGNORE) if COL_CHANNEL_IGNORE in dataset.columns else None

            for _, row in dataset.iterrows():
                if not is_ignore(row, col_ignore):
                    channelName = row.iloc[COL_CHANNEL_NAME]
                    if is_valid(channelName, VALID_PREFIXES):
                        col_customer = dataset.columns.get_loc(COL_CHANNEL_CUSTOMER) if COL_CHANNEL_CUSTOMER in dataset.columns else None
                        if col_customer:
                            reference_customers.setdefault(channelName, row.iloc[col_customer])
    except Exception:
        text = 'Failed to get dataset from Google Tables.'
        log.critical(text)
        if REPORT_RECIPIENT:
            asyncio.run(send_tg_msg(text=text, chat_id=REPORT_RECIPIENT['chat_id'], reply_to_message_id=REPORT_RECIPIENT['msg_id'], token=creds.tg[vars.BOT_NAME].token))
        raise

    # Get probe dataset from MCP

    try:
        mcp = McpAPI(creds)

        probe_customers = dict()

        get = mcp.get_fres(serviceClass=['Transport Client'], limit=SEARCH_LIMIT)
        if get.success:
            for fre in get.response.data:
                channelName = fre.attributes.displayData.displayName
                if is_valid(channelName, VALID_PREFIXES):
                    probe_customers.setdefault(prettify(channelName), {'customerName': fre.attributes.customerName, 'id': fre.id})
    except Exception:
        text = 'Failed to get dataset from MCP.'
        log.critical(text)
        if REPORT_RECIPIENT:
            asyncio.run(send_tg_msg(text=text, chat_id=REPORT_RECIPIENT['chat_id'], reply_to_message_id=REPORT_RECIPIENT['msg_id'], token=creds.tg[vars.BOT_NAME].token))
        raise

    # Comparing & fixing

    patched = 0
    for channelName, customer in reference_customers.items():
        counterpart = probe_customers.get(channelName, None)
        if counterpart and customer and customer != counterpart.get('customerName'):
            patch = mcp.patch_fre(id_=counterpart.get('id'), customerName=customer)
            if patch.success:
                patched += 1

    # Find empty customers in Google dataset
    empty_reference_customers = {k for k, v in reference_customers.items() if v is None}
    if empty_reference_customers:
        text = f"Channels {', '.join(empty_reference_customers)} has no customer. Check!"
        if REPORT_RECIPIENT is None:
            for recipient in REPORT_RECIPIENTS:
                asyncio.run(send_tg_msg(text=text, chat_id=recipient, token=creds.tg[vars.BOT_NAME].token))
        else:
            asyncio.run(send_tg_msg(text=text, chat_id=REPORT_RECIPIENT['chat_id'], reply_to_message_id=REPORT_RECIPIENT['msg_id'], token=creds.tg[vars.BOT_NAME].token))

    if patched:
        text = REPORT_UNSUCCESSFUL_TXT(patched)
    else:
        text = REPORT_SUCCESSFUL_TXT

    if REPORT_RECIPIENT is None:
        for recipient in REPORT_RECIPIENTS:
            asyncio.run(send_tg_msg(text=text, chat_id=recipient, token=creds.tg[vars.BOT_NAME].token))
    else:
        asyncio.run(send_tg_msg(text=text, chat_id=REPORT_RECIPIENT['chat_id'], reply_to_message_id=REPORT_RECIPIENT['msg_id'], token=creds.tg[vars.BOT_NAME].token))
