import logging as log
import telegram.error

from interactors.Telegram import TelegramBot
from utils.utils import load_credits


if __name__ == '__main__':
    log.basicConfig(level=log.DEBUG)

    credits = load_credits()

    tg = TelegramBot(credits)

    try:
        tg.start()
    except telegram.error.TelegramError:
        log.info('Listen cancelled, stop.')
    finally:
        log.info('Listener stopped.')
