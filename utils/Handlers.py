import redis as r
import logging as log
import vars
from models.Creds import Creds
from models.GELFMessage import GELFMessage
from utils.Senders import send_tg_msg
from utils.utils import escape_html_tags


class Handler:
    def __init__(self, credits: Creds):
        self.redis_credit = credits.redis
        self.redis = None
        self.bot = credits.tg[vars.BOT_NAME]

        self.msg = None

    async def start(self):
        self.redis = r.Redis(
                host=self.redis_credit.host,
                port=self.redis_credit.port,
                db=self.redis_credit.db,
                decode_responses=True,
                charset='utf-8'
                )

    async def stop(self):
        self._clean()

    async def process(self, msg: GELFMessage) -> None:
        """

        :param msg: GELFMessage
        :return: None
        """
        log.info(f'Working on {self.msg.short_message}')

        self.msg = msg
        log.info('Validate')
        if not self._is_valid(self.msg.full_message):
            return
        log.info('Parse')
        self._parse()
        log.info('Validate')
        if not self._is_valid(self.msg_parse):
            return
        log.info('Send')
        await self._send()

    def _parse(self) -> None:
        """
        Parse msg by internal rules
        :return: None
        """
        device = self.redis.get(f'{vars.PROJECT_NAME}.mcp.devices.{self.msg.source_}.displayName')
        self.msg_parse = escape_html_tags(self.msg.short_message)

        self.msg_parse = '\n'.join(
            (
                f'{self.msg.timestamp_}',
                f'<b>{device}</b> (<code>{self.msg.source_}</code>):',
                f'{self.msg_parse}',
                )
            )

    async def _send(self) -> None:
        """
        Send parsed msg to telegram chat by chat_id
        :return: None
        """

        await send_tg_msg(
            text=self.msg_parse,
            token=self.bot.token,
            chat_id=self.bot.groups[vars.BOT_DFT_CHAT]
            )

    def _clean(self):
        self.redis.close()

    def _is_valid(self, text: str) -> bool:
        is_stop = self.redis.get(f'{vars.PROJECT_NAME}.mgmt.is_stop')
        if is_stop is not None and is_stop.isdigit() and int(is_stop) == 1:
            return False

        filter_keywords = self.redis.smembers(f'{vars.PROJECT_NAME}.mgmt.filters')

        return not any(keyword in text for keyword in filter_keywords) if filter_keywords is not None else True
