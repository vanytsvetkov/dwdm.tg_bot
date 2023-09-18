import redis as r
from models.Credits import Credits
from models.GELFMessage import GELFMessage
from utils.Senders import send_tg_msg


class Handler:
    def __init__(self, credits: Credits):
        self.redis_credit = credits.redis
        self.redis = None
        self.bot = credits.tg['@GBL_DWDM_Monitoring_Bot']

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
        self.msg = msg
        if not self._is_valid(self.msg.full_message):
            return

        self._parse()

        if not self._is_valid(self.msg_parse):
            return

        await self._send()

    def _parse(self) -> None:
        """
        Parse msg by internal rules
        :return: None
        """
        device = self.redis.get(f'dwdm.tg_bot.mcp.devices.{self.msg.source_}.displayName')
        self.msg_parse = self.msg.short_message.replace('<', '&lt;').replace('>', '&gt;')

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
            chat_id=self.bot.users['@f1rs_t']
            )

    def _clean(self):
        self.redis.close()

    def _is_valid(self, text: str) -> bool:
        is_stop = self.redis.get('dwdm.tg_bot.mgmt.is_stop')
        if is_stop and is_stop.isdigit() and int(is_stop) == 1:
            return False

        filter_keywords = self.redis.smembers('dwdm.tg_bot.mgmt.filters')
        if not filter_keywords:
            return True

        return not any(keyword in text for keyword in filter_keywords)
