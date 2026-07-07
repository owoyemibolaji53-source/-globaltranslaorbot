"""
Database management for GlobalTranslaorBot
Uses TinyDB for lightweight, file-based storage
"""

import json
from typing import Dict, List, Optional, Any
from datetime import datetime, timedelta
from tinydb import TinyDB, Query
from tinydb.operations import add
from config import Config
from utils.logger import setup_logger

logger = setup_logger(__name__)


class Database:
    """Database handler for user data and translation history"""

    def __init__(self, db_path: str = Config.DB_PATH):
        """Initialize database"""
        try:
            self.db = TinyDB(db_path)
            self.translations = self.db.table("translations")
            self.users = self.db.table("users")
            self.settings = self.db.table("settings")
            logger.info(f"✅ Database initialized at {db_path}")
        except Exception as e:
            logger.error(f"❌ Database initialization failed: {str(e)}")
            raise

    # ---- User Management ----

    def get_user(self, user_id: int) -> Optional[Dict]:
        """Get user data from database"""
        User = Query()
        result = self.users.get(User.id == user_id)
        if not result:
            # Create new user
            user_data = {
                "id": user_id,
                "default_lang": Config.DEFAULT_TARGET_LANGUAGE,
                "created_at": datetime.now().isoformat(),
                "total_translations": 0,
                "favorite_languages": [],
                "history": [],
            }
            self.users.insert(user_data)
            return user_data
        return result

    def update_user(self, user_id: int, data: Dict) -> None:
        """Update user data"""
        User = Query()
        self.users.update(data, User.id == user_id)

    def get_user_settings(self, user_id: int) -> Dict:
        """Get user settings"""
        user = self.get_user(user_id)
        return {
            "default_lang": user.get("default_lang", Config.DEFAULT_TARGET_LANGUAGE),
            "auto_detect": user.get("auto_detect", True),
            "save_history": user.get("save_history", True),
            "show_confidence": user.get("show_confidence", False),
        }

    def update_user_settings(self, user_id: int, settings: Dict) -> None:
        """Update user settings"""
        user = self.get_user(user_id)
        user.update(settings)
        self.update_user(user_id, user)

    # ---- Translation History ----

    def add_translation(
        self,
        user_id: int,
        source_text: str,
        translated_text: str,
        source_lang: str,
        target_lang: str,
        confidence: float = 0.0,
    ) -> None:
        """Add translation to user history"""
        try:
            user = self.get_user(user_id)

            # Check if saving history is enabled
            if not user.get("save_history", True):
                return

            # Create translation record
            translation = {
                "source_text": source_text[:500],  # Truncate for storage
                "translated_text": translated_text[:500],
                "source_lang": source_lang,
                "target_lang": target_lang,
                "confidence": confidence,
                "timestamp": datetime.now().isoformat(),
            }

            # Add to history (keep last 100)
            history = user.get("history", [])
            history.append(translation)
            if len(history) > 100:
                history = history[-100:]

            # Update user
            user["history"] = history
            user["total_translations"] = user.get("total_translations", 0) + 1

            # Update favorite languages
            favorites = user.get("favorite_languages", [])
            if target_lang in favorites:
                favorites.remove(target_lang)
            favorites.insert(0, target_lang)
            if len(favorites) > 10:
                favorites = favorites[:10]
            user["favorite_languages"] = favorites

            self.update_user(user_id, user)

        except Exception as e:
            logger.error(f"Failed to add translation to history: {str(e)}")

    def get_history(self, user_id: int, limit: int = 10) -> List[Dict]:
        """Get user translation history"""
        user = self.get_user(user_id)
        history = user.get("history", [])
        return history[-limit:]

    def clear_history(self, user_id: int) -> None:
        """Clear user translation history"""
        user = self.get_user(user_id)
        user["history"] = []
        self.update_user(user_id, user)

    def get_stats(self, user_id: int) -> Dict:
        """Get user statistics"""
        user = self.get_user(user_id)
        history = user.get("history", [])

        # Count languages used
        languages_used = {}
        for entry in history:
            lang = entry.get("target_lang", "unknown")
            languages_used[lang] = languages_used.get(lang, 0) + 1

        # Get most used language
        most_used = max(languages_used.items(), key=lambda x: x[1])[0] if languages_used else None

        return {
            "total_translations": user.get("total_translations", 0),
            "languages_used": len(languages_used),
            "most_used_language": most_used,
            "history_count": len(history),
            "favorite_languages": user.get("favorite_languages", []),
        }

    # ---- Cleanup ----

    def cleanup_old_records(self, days: int = 30) -> None:
        """Remove translation records older than specified days"""
        try:
            cutoff = datetime.now() - timedelta(days=days)
            cutoff_str = cutoff.isoformat()

            # Remove old translations from all users
            for user in self.users.all():
                history = user.get("history", [])
                new_history = [
                    h for h in history
                    if h.get("timestamp", "") >= cutoff_str
                ]
                if len(new_history) != len(history):
                    user["history"] = new_history
                    self.update_user(user["id"], user)

            logger.info(f"🧹 Cleaned up records older than {days} days")
        except Exception as e:
            logger.error(f"Cleanup failed: {str(e)}")
