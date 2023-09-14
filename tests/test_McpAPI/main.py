import os
import json
from models.Credits import Credits
from interactors.McpAPI import McpAPI

DATA_DIR = 'data'
CREDITS_FILENAME = 'credentials.json'

current_dir = os.path.dirname(os.path.abspath(__file__))
tests = os.path.dirname(current_dir)
base = os.path.dirname(tests)

with open(os.path.join(base, DATA_DIR, CREDITS_FILENAME)) as credits_file:
    credits = Credits.model_validate(json.load(credits_file))
del credits_file

mcp = McpAPI(credits)

print(mcp)
