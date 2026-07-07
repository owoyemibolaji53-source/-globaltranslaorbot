"""
Handles all translation-related commands and messages
"""

import asyncio
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes
from telegram.constants import ParseMode
from config import Config
from database import Database
from services.translation_service import TranslationService
from services.language_service import LanguageService
from utils.validators import validate_text_length, sanitize_input
from utils.formatters import format_translation_result
from keyboards.inline_keyboards import get_translation_keyboard
from utils.logger import setup_logger

logger = setup_logger(__name__)

# Conversation states
SELECTING_LANGUAGE = 1


async def translate_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """
    Handle /translate command
    Usage: /translate [target_lang] [text]
    Examples:
        /translate es Hello world
        /translate Hello world (uses default language)
    """
    try:
        text = " ".join(context.args)

        if not text:
            # Check if replying to a message
            if update.message.reply_to_message:
                await handle_reply_translation(update, context)
                return

            await update.message.reply_text(
                "❌ **Please provide text to translate**\n\n"
                "Examples:\n"
                "• `/translate es Hello` - Translate to Spanish\n"
                "• `/translate Hello` - Use your default language\n"
                "• Reply to a message with `/translate`",
                parse_mode=ParseMode.MARKDOWN,
            )
            return

        # Parse target language if provided
        words = text.split()
        target_lang = context.user_data.get("default_lang", Config.DEFAULT_TARGET_LANGUAGE)

        # Check if first word is a valid language code
        if len(words) >= 2 and Config.is_supported(words[0]):
            target_lang = words[0]
            text_to_translate = " ".join(words[1:])
        else:
            text_to_translate = text

        # Validate text length
        if not validate_text_length(text_to_translate):
            await update.message.reply_text(
                f"⚠️ Text is too long. Maximum {Config.MAX_TRANSLATION_LENGTH} characters."
            )
            return

        # Send processing message
        processing_msg = await update.message.reply_text("🔄 Translating...")

        # Perform translation
        result = await TranslationService.translate_text(
            text_to_translate, target_lang
        )

        # Save to history
        db = context.bot_data.get("db")
        if db:
            db.add_translation(
                user_id=update.effective_user.id,
                source_text=text_to_translate,
                translated_text=result["translated_text"],
                source_lang=result["detected_language"],
                target_lang=target_lang,
                confidence=result.get("confidence", 0.0),
            )

        # Delete processing message
        await processing_msg.delete()

        # Format and send result
        formatted_result = format_translation_result(
            result, text_to_translate, target_lang
        )

        await update.message.reply_text(
            formatted_result,
            reply_markup=get_translation_keyboard(result),
            parse_mode=ParseMode.MARKDOWN,
        )

    except Exception as e:
        logger.error(f"Translate command error: {str(e)}")
        await update.message.reply_text(
            f"❌ **Translation failed**\n\n{str(e)}",
            parse_mode=ParseMode.MARKDOWN,
        )


async def handle_text_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle regular text messages - auto-translate"""
    try:
        text = update.message.text

        # Skip if message is too short (probably not intended for translation)
        if len(text.strip()) < 2:
            return

        # Skip if user doesn't want auto-translation
        user_settings = context.user_data.get("settings", {})
        if not user_settings.get("auto_translate", True):
            return

        # Get user settings
        user_id = update.effective_user.id
        db = context.bot_data.get("db")
        if db:
            user_data = db.get_user(user_id)
            target_lang = user_data.get("default_lang", Config.DEFAULT_TARGET_LANGUAGE)
        else:
            target_lang = context.user_data.get("default_lang", Config.DEFAULT_TARGET_LANGUAGE)

        # Show typing indicator
        await update.message.chat.send_action(action="typing")

        # Perform translation
        result = await TranslationService.translate_text(text, target_lang)

        # Check if source and target are the same
        if result["detected_language"] == target_lang:
            await update.message.reply_text(
                f"📝 **Detected Language:** {Config.get_language_name(target_lang)}\n"
                f"💡 Text is already in your default language.\n"
                f"Use `/setlang [code]` to change your target language.",
                parse_mode=ParseMode.MARKDOWN,
            )
            return

       
