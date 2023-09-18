import json
import sys
import os
from models.Credits import Credits


PROJECT_NAME = 'dwdm.tg_bot'
DATA_DIR = 'data'
CREDITS_FILENAME = 'credentials.json'
NECESSARY_FILES = [CREDITS_FILENAME]


def load_credits() -> Credits:

    current_dir = os.path.dirname(os.path.abspath(__file__))
    if PROJECT_NAME not in current_dir:
        log.critical(f'Please ensure that scripts is running with project-name "{PROJECT_NAME}" in path.')
        sys.exit(0)

    while not current_dir.endswith(PROJECT_NAME):
        current_dir = os.path.dirname(current_dir)
    else:
        base = current_dir

    if not all(os.path.exists(os.path.join(base, DATA_DIR, file)) for file in NECESSARY_FILES):
        log.critical(f'Please ensure that all required files are located in the "{DATA_DIR}" directory.')
        sys.exit(0)

    with open(os.path.join(base, DATA_DIR, CREDITS_FILENAME)) as credits_file:
        credits = Credits.model_validate(json.load(credits_file))

    return credits
