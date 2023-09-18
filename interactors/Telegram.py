import vars
import redis as r
from telegram import Update
from telegram.ext import Application, CommandHandler, ContextTypes, filters
from models.Credits import Credits


async def cmd_report(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    pass


async def cmd_check(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    pass


async def cmd_sync(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    pass


class TelegramBot:
    def __init__(self, credits: Credits):
        self.bot = credits.tg[vars.BOT_NAME]
        self.allowed_chats = filters.Chat(
            chat_id={
                *self.bot.users.values(),
                *self.bot.groups.values()
                }
            )

        self.application = Application.builder().token(self.bot.token).build()

        self.redis = r.Redis(
                host=credits.redis.host,
                port=credits.redis.port,
                db=credits.redis.db,
                decode_responses=True,
                charset='utf-8'
            )

    def start(self) -> None:
        self.add_handlers()
        self.application.run_polling(allowed_updates=Update.MESSAGE)

    def add_handlers(self):
        self.application.add_handler(CommandHandler("show", self.cmd_show, filters=self.allowed_chats, has_args=False))
        self.application.add_handler(CommandHandler("report", cmd_report, filters=self.allowed_chats, has_args=False))
        self.application.add_handler(CommandHandler("check", cmd_check, filters=self.allowed_chats, has_args=False))
        self.application.add_handler(CommandHandler("sync", cmd_sync, filters=self.allowed_chats, has_args=False))
        self.application.add_handler(CommandHandler("filter", self.cmd_filter, filters=self.allowed_chats, has_args=True))
        self.application.add_handler(CommandHandler("delete", self.cmd_delete, filters=self.allowed_chats, has_args=True))
        self.application.add_handler(CommandHandler("start", self.cmd_start, filters=self.allowed_chats, has_args=False))
        self.application.add_handler(CommandHandler("stop", self.cmd_stop, filters=self.allowed_chats, has_args=False))

    async def cmd_show(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
        filter_keywords = self.redis.smembers('dwdm.tg_bot.mgmt.filters')
        if filter_keywords:
            output = 'Keyword & [Reason]:\n\n'
            output += '\n'.join(f"{i+1}. <code>{keyword.replace('<', '&lt;').replace('>', '&gt;')}</code>" for i, keyword in enumerate(filter_keywords))
        else:
            output = 'Nothing is ignored in this chat'

        await update.message.reply_text(output, parse_mode='HTML')

    async def cmd_filter(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
        keyword = ' '.join(context.args)
        if keyword:
            await self.redis.sadd('dwdm.tg_bot.mgmt.filters', keyword)

    async def cmd_delete(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
        keyword = ' '.join(context.args)
        if keyword:
            await self.redis.srem('dwdm.tg_bot.mgmt.filters', keyword)

    async def cmd_stop(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
        await self.redis.set('dwdm.tg_bot.mgmt.is_stop', 1)

    async def cmd_start(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
        await self.redis.set('dwdm.tg_bot.mgmt.is_stop', 0)
