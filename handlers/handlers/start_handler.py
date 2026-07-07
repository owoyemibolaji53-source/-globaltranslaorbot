"""
Handles /start and /help commands
"""

from telegram import Update
from telegram.ext import ContextTypes
from config import Config
from database import Database
from keyboards.inline_keyboards import get_main_keyboard
from utils.formatters import format_help_message
from utils.logger import setup_logger

logger = setup_logger(__name__)


async def start_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle /start command"""
    user = update.effective_user
    user_id = user.id

    # Initialize user in database
    db = context.bot_data.get("db")
    if db:
        db.get_user(user_id)

    welcome_message = f"""
🌍 **Welcome to GlobalTranslaorBot, {user.first_name}!**

I'm your powerful AI-powered translation assistant. I can translate between **{len(Config.SUPPORTED_LANGUAGES)} languages** instantly!

🚀 **Quick Start:**
• Send me any text message → Auto-translate to your default language
• Use `/translate [lang] [text]` → Translate to specific language
• Reply to any message with `/translate` → Translate replied message
• Forward any message → Auto-translate it

📌 **Useful Commands:**
• `/help` - Show all available commands
• `/languages` - List all supported languages
• `/detect` - Detect language of text
• `/history` - View your translation history
• `/settings` - Configure bot preferences

💡 **Tips:**
• Set your default language with `/setlang [code]`
• Example: `/setlang es` for Spanish
• Auto-detect source language works for all supported languages

Powered by Google Translate 🤖
"""

    await update.message.reply_text(
        welcome_message,
        reply_markup=get_main_keyboard(),
        parse_mode="Markdown",
    )

    logger.info(f"User {user_id} ({user.username}) started the bot")


async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle /help command"""
    help_text = format_help_message()

    await update.message.reply_text(
        help_text,
        parse_mode="Markdown",
    )

    logger.debug(f"User {update.effective_user.id} requested help")
