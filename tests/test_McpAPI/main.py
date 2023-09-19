from interactors.McpAPI import McpAPI
import logging
from utils.utils import load_creds

logging.basicConfig(level=logging.DEBUG)

credits = load_creds()

mcp = McpAPI(credits)

# token = mcp.get_token()

# networkConstructs = mcp.get_networkConstructs()

ciena_6500 = mcp.get_Ciena6500()
