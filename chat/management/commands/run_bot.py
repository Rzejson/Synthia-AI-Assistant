import os
from asgiref.sync import sync_to_async
from django.core.management.base import BaseCommand
from django.conf import settings
from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, ContextTypes, filters
from chat.services.orchestrator import ConversationOrchestrator
from chat.models import Conversation, Message


class Command(BaseCommand):
    def process_telegram_message(self, user_id, user_text):
        conversation, created = Conversation.objects.get_or_create(topic=user_id)
        Message.objects.create(
            conversation=conversation,
            role='user',
            content=user_text,
        )
        orchestrator = ConversationOrchestrator(conversation)
        response = orchestrator.handle_message(user_text)
        return response

    def check_auth(self, update: Update) -> bool:
        user_id = update.effective_user.id
        allowed_user_id = settings.TELEGRAM_ALLOWED_USER_ID

        if str(user_id) != allowed_user_id:
            print(f'DEBUG: Unauthorized connection attempt. User ID: {user_id}.')
            return False
        return True

    async def start(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        if not self.check_auth(update):
            return

        print(f'DEBUG: The bot has been launched.')
        await context.bot.send_message(chat_id=update.effective_chat.id, text="System: Ready to work.")

    async def handle_message(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        if not self.check_auth(update):
            return

        user_text = update.message.text
        user_id = str(update.effective_user.id)

        print(f"DEBUG: Processing message from {user_id}: {user_text}")

        await context.bot.send_chat_action(chat_id=update.effective_chat.id, action='typing')

        run_async = sync_to_async(self.process_telegram_message)
        response = await run_async(user_id, user_text)
        await context.bot.send_message(chat_id=update.effective_chat.id, text=response)

    def handle(self, *args, **options):
        token = settings.TELEGRAM_BOT_TOKEN

        app = ApplicationBuilder().token(token).build()
        app.add_handler(CommandHandler('start', self.start))
        app.add_handler(MessageHandler(filters.TEXT & (~filters.COMMAND), self.handle_message))

        print('DEBUG: Bot is listening')

        app.run_polling()
