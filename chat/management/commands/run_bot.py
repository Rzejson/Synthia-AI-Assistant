import telegram.constants
import io
from asgiref.sync import sync_to_async
from django.core.management.base import BaseCommand
from django.conf import settings
from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, ContextTypes, filters
from chat.services.orchestrator import ConversationOrchestrator
from chat.services.llm_factory import OpenAIService
from chat.models import Conversation, Message


class Command(BaseCommand):
    """
    Django's management command to start the Telegram bot.
    Handles lifecycle of the bot, processes updates, and routes messages to the Orchestrator.
    """
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
        """
        Security check. Verifies if the incoming message comes from the allowed user ID
        defined in settings.TELEGRAM_ALLOWED_USER_ID.
        """
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
        """
        Handles standard text messages.
        Passes the text directly to the conversation orchestrator.
        """
        if not self.check_auth(update):
            return

        user_text = update.message.text
        user_id = str(update.effective_user.id)

        print(f"DEBUG: Processing message from {user_id}: {user_text}")

        await context.bot.send_chat_action(
            chat_id=update.effective_chat.id,
            action=telegram.constants.ChatAction.TYPING
        )

        run_async = sync_to_async(self.process_telegram_message)
        response = await run_async(user_id, user_text)
        await context.bot.send_message(chat_id=update.effective_chat.id, text=response)

    async def handle_voice(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """
        Handles voice messages.

        1. Downloads the voice file from Telegram servers to an in-memory buffer (io.BytesIO).
        2. Sends the audio buffer to OpenAI Whisper API for transcription.
        3. Passes the transcribed text to the orchestrator as if it were a text message.
        """
        if not self.check_auth(update):
            return

        user_id = str(update.effective_user.id)

        await context.bot.send_chat_action(
            chat_id=update.effective_chat.id,
            action=telegram.constants.ChatAction.TYPING
        )

        print(f"DEBUG: Transcribing voice from {user_id}")

        user_audio = await update.message.voice.get_file()
        memory_buffer = io.BytesIO()
        await user_audio.download_to_memory(out=memory_buffer)
        memory_buffer.seek(0)
        memory_buffer.name = 'voice.oga'

        def perform_transcription():
            service = OpenAIService()
            return service.transcribe_audio(memory_buffer)
        transcribe_async = sync_to_async(perform_transcription)
        transcription = await transcribe_async()

        print(f"DEBUG: Processing a transcribed message")

        run_async = sync_to_async(self.process_telegram_message)
        response = await run_async(user_id, transcription)
        await context.bot.send_message(chat_id=update.effective_chat.id, text=response)

    def handle(self, *args, **options):
        token = settings.TELEGRAM_BOT_TOKEN

        app = ApplicationBuilder().token(token).build()
        app.add_handler(CommandHandler('start', self.start))
        app.add_handler(MessageHandler(filters.TEXT & (~filters.COMMAND), self.handle_message))
        app.add_handler(MessageHandler(filters.VOICE, self.handle_voice))

        print('DEBUG: Bot is listening')

        app.run_polling()
