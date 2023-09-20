import subprocess
import vars
import redis as r
from telegram import Update
from telegram.ext import Application, CommandHandler, ContextTypes, filters
from models.Creds import Creds
from utils.utils import escape_html_tags


async def cmd_report(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    try:
        subprocess.run([f'{vars.BASE}/scripts/RouteComparator/run.sh', f'{update.message.chat_id}', f'{update.message.message_id}'])
    except Exception as e:
        await update.message.reply_text(f'<b>An error occurred.</b>\n<i>{str(e)}</i>', parse_mode='HTML', reply_to_message_id=update.message.message_id)
    else:
        await update.message.reply_text('Your request has been accepted. Please wait for the result.', parse_mode='HTML', reply_to_message_id=update.message.message_id)


async def cmd_check(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    try:
        subprocess.run([f'{vars.BASE}/scripts/ChannelChecker/run.sh', f'{update.message.message_id}'])
    except Exception as e:
        await update.message.reply_text(f'<b>An error occurred.</b>\n<i>{str(e)}</i>', parse_mode='HTML', reply_to_message_id=update.message.message_id)
    else:
        await update.message.reply_text('Your request has been accepted. Please wait for the result.', parse_mode='HTML', reply_to_message_id=update.message.message_id)


async def cmd_sync(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    try:
        subprocess.run([f'{vars.BASE}/scripts/CustomerSyncer/run.sh', f'{update.message.message_id}'])
    except Exception as e:
        await update.message.reply_text(f'<b>An error occurred.</b>\n<i>{str(e)}</i>', parse_mode='HTML', reply_to_message_id=update.message.message_id)
    else:
        await update.message.reply_text('Your request has been accepted. Please wait for the result.', parse_mode='HTML', reply_to_message_id=update.message.message_id)


async def cmd_update(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    try:
        subprocess.run([f'{vars.BASE}/scripts/UpdateProcessor/run.sh', f'{update.message.message_id}'])
    except Exception as e:
        await update.message.reply_text(f'<b>An error occurred.</b>\n<i>{str(e)}</i>', parse_mode='HTML', reply_to_message_id=update.message.message_id)
    else:
        await update.message.reply_text('Your request has been accepted. Please wait for the result.', parse_mode='HTML', reply_to_message_id=update.message.message_id)


async def cmd_help(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    output = "Sorry, I can't help you."
    await update.message.reply_text(output, parse_mode='HTML', reply_to_message_id=update.message.message_id)


class TelegramBot:
    def __init__(self, credits: Creds):
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
        self.application.add_handler(CommandHandler("help", cmd_help, filters=self.allowed_chats, has_args=False))
        self.application.add_handler(CommandHandler("show", self.cmd_show, filters=self.allowed_chats, has_args=False))
        self.application.add_handler(CommandHandler("report", cmd_report, filters=self.allowed_chats, has_args=False))
        self.application.add_handler(CommandHandler("check", cmd_check, filters=self.allowed_chats, has_args=False))
        self.application.add_handler(CommandHandler("sync", cmd_sync, filters=self.allowed_chats, has_args=False))
        self.application.add_handler(CommandHandler("update", cmd_update, filters=self.allowed_chats, has_args=False))
        self.application.add_handler(CommandHandler("filter", self.cmd_filter, filters=self.allowed_chats, has_args=True))
        self.application.add_handler(CommandHandler("delete", self.cmd_delete, filters=self.allowed_chats, has_args=True))
        self.application.add_handler(CommandHandler("start", self.cmd_start, filters=self.allowed_chats, has_args=False))
        self.application.add_handler(CommandHandler("stop", self.cmd_stop, filters=self.allowed_chats, has_args=False))

    async def cmd_show(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
        filter_keywords = self.redis.smembers(f'{vars.PROJECT_NAME}.mgmt.filters')
        if filter_keywords:
            output = 'Keyword & [Reason]:\n\n'
            output += '\n'.join(f"{i+1}. <code>{escape_html_tags(keyword)}</code>" for i, keyword in enumerate(filter_keywords))
        else:
            output = 'Nothing is ignored in this chat'

        await update.message.reply_text(output, parse_mode='HTML', reply_to_message_id=update.message.message_id)

    async def cmd_filter(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
        keyword = ' '.join(context.args)
        if keyword:
            self.redis.sadd(f'{vars.PROJECT_NAME}.mgmt.filters', keyword)

        output = f'Keyword "<code>{escape_html_tags(keyword)}</code>" is filtered.'
        await update.message.reply_text(output, parse_mode='HTML', reply_to_message_id=update.message.message_id)

    async def cmd_delete(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
        keyword = ' '.join(context.args)
        if keyword:
            self.redis.srem(f'{vars.PROJECT_NAME}.mgmt.filters', keyword)

        output = f'Keyword "<code>{escape_html_tags(keyword)}</code>" is removed.'
        await update.message.reply_text(output, parse_mode='HTML', reply_to_message_id=update.message.message_id)

    async def cmd_stop(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
        self.redis.set(f'{vars.PROJECT_NAME}.mgmt.is_stop', 1)
        await update.message.reply_text('Bot has been stopped.', parse_mode='HTML', reply_to_message_id=update.message.message_id)

    async def cmd_start(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
        self.redis.set(f'{vars.PROJECT_NAME}.mgmt.is_stop', 0)
        await update.message.reply_text('Bot has been started.', parse_mode='HTML', reply_to_message_id=update.message.message_id)
