import json
import os
from typing import Dict, Optional
from functools import lru_cache


class TranslationManager:
    """Translation manager for internationalization"""

    def __init__(self, locales_path: str = "app/locales"):
        self.locales_path = locales_path
        self.current_language = "en"
        self._translations: Dict[str, Dict[str, str]] = {}
        self._load_translations()

    def _load_translations(self):
        """Load translation files"""
        if not os.path.exists(self.locales_path):
            os.makedirs(self.locales_path, exist_ok=True)
            # Create default English translations
            self._create_default_translations()

        for filename in os.listdir(self.locales_path):
            if filename.endswith(".json"):
                lang_code = filename[:-5]  # Remove .json extension
                file_path = os.path.join(self.locales_path, filename)
                try:
                    with open(file_path, "r", encoding="utf-8") as f:
                        self._translations[lang_code] = json.load(f)
                except (json.JSONDecodeError, IOError) as e:
                    print(f"Error loading translation file {filename}: {e}")

    def _create_default_translations(self):
        """Create default translation files"""
        default_translations = {
            "success": "Operation completed successfully",
            "error": "An error occurred",
            "not_found": "Resource not found",
            "validation_error": "Validation failed",
            "unauthorized": "Unauthorized access",
            "forbidden": "Access forbidden",
            "user_not_found": "User not found",
            "organization_not_found": "Organization not found",
            "project_not_found": "Project not found",
            "bot_not_found": "Bot not found",
            "job_not_found": "Job not found",
            "invalid_credentials": "Invalid credentials",
            "token_expired": "Token has expired",
            "insufficient_permissions": "Insufficient permissions",
            "invalid_email_format": "Invalid email format",
            "password_too_weak": "Password is too weak",
            "email_already_exists": "Email already exists",
            "username_already_exists": "Username already exists",
        }

        # Create English translations
        en_path = os.path.join(self.locales_path, "en.json")
        with open(en_path, "w", encoding="utf-8") as f:
            json.dump(default_translations, f, indent=2, ensure_ascii=False)

        # Create Vietnamese translations
        vi_translations = {
            "success": "Thao tác thành công",
            "error": "Đã xảy ra lỗi",
            "not_found": "Không tìm thấy tài nguyên",
            "validation_error": "Validation thất bại",
            "unauthorized": "Truy cập không được phép",
            "forbidden": "Quyền truy cập bị từ chối",
            "user_not_found": "Không tìm thấy người dùng",
            "organization_not_found": "Không tìm thấy tổ chức",
            "project_not_found": "Không tìm thấy dự án",
            "bot_not_found": "Không tìm thấy bot",
            "job_not_found": "Không tìm thấy công việc",
            "invalid_credentials": "Thông tin đăng nhập không hợp lệ",
            "token_expired": "Token đã hết hạn",
            "insufficient_permissions": "Không đủ quyền truy cập",
            "invalid_email_format": "Định dạng email không hợp lệ",
            "password_too_weak": "Mật khẩu quá yếu",
            "email_already_exists": "Email đã tồn tại",
            "username_already_exists": "Tên người dùng đã tồn tại",
        }

        vi_path = os.path.join(self.locales_path, "vi.json")
        with open(vi_path, "w", encoding="utf-8") as f:
            json.dump(vi_translations, f, indent=2, ensure_ascii=False)

    def set_language(self, language: str):
        """Set current language"""
        if language in self._translations:
            self.current_language = language
        else:
            print(f"Language '{language}' not found, using default")

    def translate(self, key: str, language: Optional[str] = None) -> str:
        """Translate a key to current or specified language"""
        lang = language or self.current_language

        if lang in self._translations and key in self._translations[lang]:
            return self._translations[lang][key]

        # Fallback to English
        if "en" in self._translations and key in self._translations["en"]:
            return self._translations["en"][key]

        # Return the key itself if no translation found
        return key

    def get_available_languages(self) -> list:
        """Get list of available languages"""
        return list(self._translations.keys())


# Global translation manager instance
_translation_manager = TranslationManager()


def _(key: str, language: Optional[str] = None) -> str:
    """Global translation function"""
    return _translation_manager.translate(key, language)


def set_language(language: str):
    """Set global language"""
    _translation_manager.set_language(language)


def get_translation_manager() -> TranslationManager:
    """Get translation manager instance"""
    return _translation_manager
