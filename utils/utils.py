import json
import sys
import vars
import os
import logging as log
from models.Credits import Credits


def load_credits() -> Credits:

    current_dir = os.path.dirname(os.path.abspath(__file__))
    if vars.PROJECT_NAME not in current_dir:
        log.critical(f'Please ensure that scripts is running with project-name "{vars.PROJECT_NAME}" in path.')
        sys.exit(0)

    while not current_dir.endswith(vars.PROJECT_NAME):
        current_dir = os.path.dirname(current_dir)
    else:
        base = current_dir

    if not all(os.path.exists(os.path.join(base, vars.DATA_DIR, file)) for file in vars.NECESSARY_FILES):
        log.critical(f'Please ensure that all required files are located in the "{vars.DATA_DIR}" directory.')
        sys.exit(0)

    with open(os.path.join(base, vars.DATA_DIR, vars.CREDITS_FILENAME)) as credits_file:
        credits = Credits.model_validate(json.load(credits_file))

    return credits
