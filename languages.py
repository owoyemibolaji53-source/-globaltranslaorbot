"""
Language definitions for GlobalTranslaorBot
"""

from config import Config

# Language codes and names mapping
LANGUAGES = Config.SUPPORTED_LANGUAGES

# Common language codes for quick access
COMMON_LANGUAGES = {
    "en": "English",
    "es": "Spanish",
    "fr": "French",
    "de": "German",
    "it": "Italian",
    "pt": "Portuguese",
    "ru": "Russian",
    "zh": "Chinese",
    "ja": "Japanese",
    "ko": "Korean",
    "ar": "Arabic",
    "hi": "Hindi",
    "yo": "Yoruba",
    "ha": "Hausa",
    "ig": "Igbo",
    "sw": "Swahili",
}

# Language names in their native language (for display)
NATIVE_NAMES = {
    "en": "English",
    "es": "Español",
    "fr": "Français",
    "de": "Deutsch",
    "it": "Italiano",
    "pt": "Português",
    "ru": "Русский",
    "zh": "中文",
    "ja": "日本語",
    "ko": "한국어",
    "ar": "العربية",
    "hi": "हिन्दी",
    "yo": "Èdè Yorùbá",
    "ha": "Hausa",
    "ig": "Igbo",
    "sw": "Kiswahili",
}


def get_language_name(code: str, native: bool = False) -> str:
    """Get language name for a code"""
    if native and code in NATIVE_NAMES:
        return NATIVE_NAMES[code]
    return LANGUAGES.get(code, code)


def get_language_code(name: str) -> str:
    """Get language code from name (case-insensitive)"""
    name_lower = name.lower()
    for code, lang_name in LANGUAGES.items():
        if lang_name.lower() == name_lower:
            return code
    return None


def get_common_languages() -> dict:
    """Get list of common languages"""
    return COMMON_LANGUAGES


def get_all_languages() -> dict:
    """Get all supported languages"""
    return LANGUAGES


def get_language_emoji(code: str) -> str:
    """Get emoji flag for language (if available)"""
    flags = {
        "en": "🇬🇧",
        "es": "🇪🇸",
        "fr": "🇫🇷",
        "de": "🇩🇪",
        "it": "🇮🇹",
        "pt": "🇵🇹",
        "ru": "🇷🇺",
        "zh": "🇨🇳",
        "ja": "🇯🇵",
        "ko": "🇰🇷",
        "ar": "🇸🇦",
        "hi": "🇮🇳",
        "yo": "🇳🇬",
        "ha": "🇳🇬",
        "ig": "🇳🇬",
        "sw": "🇹🇿",
        "fr": "🇫🇷",
        "de": "🇩🇪",
        "it": "🇮🇹",
        "nl": "🇳🇱",
        "pl": "🇵🇱",
        "uk": "🇺🇦",
        "vi": "🇻🇳",
        "th": "🇹🇭",
        "id": "🇮🇩",
        "ms": "🇲🇾",
        "tl": "🇵🇭",
    }
    return flags.get(code, "🌍")
