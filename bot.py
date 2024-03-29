import logging as log

import vars
from interactors.Telegram import TelegramBot
from utils.utils import load_creds

if __name__ == '__main__':
    log.basicConfig(level=vars.LOG_LEVEL)

    credits = load_creds()

    tg = TelegramBot(credits)

    try:
        tg.start()
    finally:
        log.info('Listener stopped.')
