from models.Credits import Credits
from models.GELFMessage import GELFMessage
from utils.Senders import send_tg_msg
import logging as log


class Handler:
    def __init__(self, credits: Credits):
        self.bot = credits.tg['@GBL_DWDM_Monitoring_Bot']

        self.msg = None

    async def start(self) -> None:
        """
        :return: None
        """
        pass

    async def stop(self) -> None:
        """

        :return:  None
        """
        pass

    async def process(self, msg: GELFMessage) -> None:
        """

        :param msg: GELFMessage
        :return: None
        """
        self.msg = msg
        self._parse()
        await self._send()

    def _parse(self) -> None:
        """

        :return: None
        """
        self.msg_parse = str(self.msg)
        if "<" in self.msg_parse:
            self.msg_parse = self.msg_parse.replace("<", "&lt;")
        if ">" in self.msg_parse:
            self.msg_parse = self.msg_parse.replace(">", "&gt;")

    async def _send(self) -> None:
        """

        :return: None
        """

        await send_tg_msg(
            text=self.msg_parse,
            token=self.bot.token,
            chat_id=self.bot.users['@f1rs_t']
            )
