import os
import sys
import logging as log


def get_base() -> str:
    current_dir = os.path.dirname(os.path.abspath(__file__))
    if PROJECT_NAME not in current_dir:
        log.critical(f'Please ensure that scripts is running with project-name "{PROJECT_NAME}" in path.')
        sys.exit(0)

    while not current_dir.endswith(PROJECT_NAME):
        current_dir = os.path.dirname(current_dir)
    else:
        base = current_dir

    return base


PROJECT_NAME = 'dwdm.tg_bot'

BASE = get_base()
DATA_DIR = 'data'

CREDITS_FILENAME = 'credentials.json'
GOOGLE_API_FILENAME = 'api-project.json'

NECESSARY_FILES = [CREDITS_FILENAME, GOOGLE_API_FILENAME]

LOG_LEVEL = 'INFO'

# BOT_NAME = '@GBL_DWDM_Monitoring_Bot'
BOT_NAME = '@ArborSightlineBot'
BOT_DFT_CHAT = '@f1rs_t'
