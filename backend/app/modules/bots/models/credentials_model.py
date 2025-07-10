import base64
import json
import os
import random
import string
from typing import Any, Dict, Optional
from uuid import UUID

from cryptography.fernet import Fernet
from sqlmodel import Field, Relationship

from app.core.base_enums import CredentialTypes
from app.core.base_model import BaseEntity


class Credentials(BaseEntity, table=True):
    __tablename__ = "credentials"

    # Core fields
    project_id: UUID = Field(foreign_key="project.id", index=True)
    credential_type: CredentialTypes = Field(index=True)

    # Encrypted credentials storage
    encrypted_credentials: Optional[bytes] = Field(default=None)

    # Metadata
    description: Optional[str] = Field(default=None, max_length=500)
    is_active: bool = Field(default=True)

    # Auto-generated object_id
    object_id: str = Field(
        default_factory=lambda: "cred_" + "".join(random.choices(string.ascii_letters + string.digits, k=16)),
        unique=True,
        max_length=32,
        index=True,
    )

    # Relationships
    project: "Project" = Relationship(back_populates="credentials")

    @property
    def encryption_key(self) -> bytes:
        """Get encryption key from environment variable"""
        key_str = os.getenv("CREDENTIALS_ENCRYPTION_KEY")
        if not key_str:
            raise ValueError("CREDENTIALS_ENCRYPTION_KEY environment variable not set")
        return key_str.encode()

    def set_credentials(self, credentials: Dict[str, Any]) -> None:
        """Encrypt and store credentials"""
        if not credentials:
            self.encrypted_credentials = None
            return

        # Convert to JSON string
        credentials_json = json.dumps(credentials)

        # Encrypt
        fernet = Fernet(base64.urlsafe_b64encode(self.encryption_key[:32]))
        encrypted_data = fernet.encrypt(credentials_json.encode())

        self.encrypted_credentials = encrypted_data

    def get_credentials(self) -> Optional[Dict[str, Any]]:
        """Decrypt and return credentials"""
        if not self.encrypted_credentials:
            return None

        try:
            # Decrypt
            fernet = Fernet(base64.urlsafe_b64encode(self.encryption_key[:32]))
            decrypted_data = fernet.decrypt(self.encrypted_credentials)

            # Parse JSON
            credentials_json = decrypted_data.decode()
            return json.loads(credentials_json)

        except Exception as e:
            # Log error but don't expose sensitive info
            print(f"Failed to decrypt credentials for {self.object_id}: {type(e).__name__}")
            return None

    def has_credentials(self) -> bool:
        """Check if credentials are set"""
        return self.encrypted_credentials is not None

    def get_credential_type_display(self) -> str:
        """Get human-readable credential type"""
        type_names = {
            CredentialTypes.DEEPGRAM: "Deepgram",
            CredentialTypes.ZOOM_OAUTH: "Zoom OAuth",
            CredentialTypes.GOOGLE_TEXT_TO_SPEECH: "Google Text-to-Speech",
            CredentialTypes.GLADIA: "Gladia",
            CredentialTypes.OPENAI: "OpenAI",
            CredentialTypes.ASSEMBLY_AI: "AssemblyAI",
            CredentialTypes.SARVAM: "Sarvam",
        }
        return type_names.get(self.credential_type, str(self.credential_type.value))

    def validate_credentials(self) -> tuple[bool, Optional[str]]:
        """Validate credentials format based on type"""
        credentials = self.get_credentials()
        if not credentials:
            return False, "No credentials found"

        try:
            if self.credential_type == CredentialTypes.DEEPGRAM:
                if "api_key" not in credentials:
                    return False, "Missing api_key"
                if not credentials["api_key"].strip():
                    return False, "api_key is empty"

            elif self.credential_type == CredentialTypes.OPENAI:
                if "api_key" not in credentials:
                    return False, "Missing api_key"
                if not credentials["api_key"].strip():
                    return False, "api_key is empty"

            elif self.credential_type == CredentialTypes.GLADIA:
                if "api_key" not in credentials:
                    return False, "Missing api_key"
                if not credentials["api_key"].strip():
                    return False, "api_key is empty"

            elif self.credential_type == CredentialTypes.ASSEMBLY_AI:
                if "api_key" not in credentials:
                    return False, "Missing api_key"
                if not credentials["api_key"].strip():
                    return False, "api_key is empty"

            elif self.credential_type == CredentialTypes.SARVAM:
                if "api_key" not in credentials:
                    return False, "Missing api_key"
                if not credentials["api_key"].strip():
                    return False, "api_key is empty"

            elif self.credential_type == CredentialTypes.ZOOM_OAUTH:
                required_fields = ["client_id", "client_secret", "access_token"]
                for field in required_fields:
                    if field not in credentials:
                        return False, f"Missing {field}"
                    if not credentials[field].strip():
                        return False, f"{field} is empty"

            elif self.credential_type == CredentialTypes.GOOGLE_TEXT_TO_SPEECH:
                if "service_account_json" not in credentials:
                    return False, "Missing service_account_json"
                # Try to parse as JSON
                try:
                    json.loads(credentials["service_account_json"])
                except json.JSONDecodeError:
                    return False, "service_account_json is not valid JSON"

            return True, None

        except Exception as e:
            return False, f"Validation error: {str(e)}"

    def get_api_key(self) -> Optional[str]:
        """Get API key if this credential type uses one"""
        credentials = self.get_credentials()
        if not credentials:
            return None
        return credentials.get("api_key")

    def mask_sensitive_data(self) -> Dict[str, Any]:
        """Get credentials with sensitive data masked"""
        credentials = self.get_credentials()
        if not credentials:
            return {}

        masked = {}
        for key, value in credentials.items():
            if isinstance(value, str) and len(value) > 8:
                # Show first 4 and last 4 characters
                masked[key] = f"{value[:4]}...{value[-4:]}"
            elif isinstance(value, str) and len(value) > 0:
                masked[key] = "*" * len(value)
            else:
                masked[key] = value

        return masked

    def test_connection(self) -> tuple[bool, Optional[str]]:
        """Test if credentials work (placeholder - would implement actual API calls)"""
        # This would implement actual API testing for each provider
        if not self.has_credentials():
            return False, "No credentials configured"

        is_valid, error = self.validate_credentials()
        if not is_valid:
            return False, error

        # TODO: Implement actual API testing
        return True, "Connection test not implemented"

    def __repr__(self):
        type_name = self.get_credential_type_display()
        status = "Active" if self.is_active else "Inactive"
        has_creds = "✓" if self.has_credentials() else "✗"
        return f"<Credentials {self.object_id}: {type_name} ({status}) {has_creds}>"
