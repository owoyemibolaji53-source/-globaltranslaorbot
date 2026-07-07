#!/usr/bin/env python3
"""
GlobalTranslaorBot - Main Entry Point
A powerful Telegram bot for instant language translation
"""

import asyncio
from telegram.ext import (
    Application,
    CommandHandler,
    MessageHandler,
    CallbackQueryHandler,
    ConversationHandler,
    filters,
)
from config import Config
from database import Database
from handlers.start_handler import start_command, help_command
from handlers.translate_handler import (
    translate_command,
    handle_text_message,
    handle_reply_translation,
    handle_forwarded_message,
    detect_language_command,
    clear_history_command,
)
from handlers.language_handler import (
    languages_command,
    set_language_command,
    language_callback,
)
from handlers.history_handler import history_command
from handlers.settings_handler import settings_command, settings_callback
from handlers.error_handler import error_handler
from utils.logger import setup_logger

# Initialize logger
logger = setup_logger(__name__)


def main():
    """Main function to run the bot"""
    try:
        # Validate configuration
        Config.validate()

        # Initialize database
        db = Database()
        logger.info("✅ Database initialized")

        # Create application with built-in rate limiting
        application = (
            Application.builder()
            .token(Config.TELEGRAM_BOT_TOKEN)
            .concurrent_updates(True)
            .build()
        )

        # Store database in application context
        application.bot_data["db"] = db

        # Register command handlers
        application.add_handler(CommandHandler("start", start_command))
        application.add_handler(CommandHandler("help", help_command))
        application.add_handler(CommandHandler("languages", languages_command))
        application.add_handler(CommandHandler("detect", detect_language_command))
        application.add_handler(CommandHandler("translate", translate_command))
        application.add_handler(CommandHandler("history", history_command))
        application.add_handler(CommandHandler("settings", settings_command))
        application.add_handler(CommandHandler("setlang", set_language_command))
        application.add_handler(CommandHandler("clear", clear_history_command))

        # Message handlers (order matters!)
        # 1. Reply translation handler (when replying to a message)
        application.add_handler(
            MessageHandler(
                filters.REPLY & filters.TEXT & ~filters.COMMAND,
                handle_reply_translation,
            )
        )

        # 2. Forwarded message handler
        application.add_handler(
            MessageHandler(
                filters.FORWARDED & filters.TEXT & ~filters.COMMAND,
                handle_forwarded_message,
            )
        )

        # 3. Regular text messages
        application.add_handler(
            MessageHandler(
                filters.TEXT & ~filters.COMMAND,
                handle_text_message,
            )
        )

        # Callback query handlers (for inline keyboards)
        application.add_handler(
            CallbackQueryHandler(language_callback, pattern="^lang_")
        )
        application.add_handler(
            CallbackQueryHandler(settings_callback, pattern="^setting_")
        )
        application.add_handler(
            CallbackQueryHandler(history_command, pattern="^history_")
        )

        # Global error handler
        application.add_error_handler(error_handler)

        # Start the bot
        logger.info("🚀 GlobalTranslaorBot started successfully!")
        logger.info(f"🤖 Bot username: @{Config.BOT_USERNAME}")
        logger.info(f"🌍 Environment: {Config.ENVIRONMENT}")

        # Run the bot with graceful shutdown
        application.run_polling(
            allowed_updates=["message", "callback_query"],
            drop_pending_updates=True,
            stop_signals=None,  # Better for Railway
        )

    except KeyboardInterrupt:
        logger.info("🛑 Bot stopped by user")
    except Exception as e:
        logger.error(f"❌ Fatal error: {str(e)}")
        raise


if __name__ == "__main__":
    main()
