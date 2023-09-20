import asyncio
import json
import telegram
from telegram.error import NetworkError, RetryAfter, TimedOut


async def send_tg_msg(token: str, chat_id: int, text: str = None, caption: str = '', reply_to_message_id: int = None, parse_mode: str = "HTML", data: dict = None, filename: str = None, repeat: int = 0, **kwargs) -> int:
    bot = telegram.Bot(token)
    repeatLimit = 10

    if repeat <= repeatLimit:
        try:
            if text:
                message = await bot.send_message(text=text, chat_id=chat_id, reply_to_message_id=reply_to_message_id, parse_mode=parse_mode)
                return message.message_id

            if data:
                if isinstance(data['data'], str):
                    document = data['data'].encode('utf-8')
                elif isinstance(data['data'], bytes):
                    document = data['data']
                else:
                    document = json.dumps(data["data"], indent=4, default=str).encode('utf-8')

                message = await bot.send_document(caption=caption, chat_id=chat_id, document=document, reply_to_message_id=reply_to_message_id, filename=data["filename"], parse_mode=parse_mode)
                return message.message_id

            if filename:
                message = await bot.send_photo(caption=caption, chat_id=chat_id, photo=open(filename, "rb"), reply_to_message_id=reply_to_message_id, parse_mode=parse_mode)
                return message.message_id

        except RetryAfter as retry:
            await asyncio.sleep(retry.retry_after)
            return await send_tg_msg(token, chat_id, text, caption, reply_to_message_id, parse_mode, data, repeat+1, **kwargs)
        except TimedOut:
            await asyncio.sleep(10)
            return await send_tg_msg(token, chat_id, text, caption, reply_to_message_id, parse_mode, data, repeat+1, **kwargs)
        except NetworkError:
            return 0
