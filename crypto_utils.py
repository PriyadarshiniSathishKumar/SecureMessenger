import os
from cryptography.fernet import Fernet
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
import base64
import logging

logger = logging.getLogger(__name__)

class CryptoManager:
    def __init__(self):
        """Initialize the crypto manager with a master key"""
        self.master_key = self._load_or_generate_master_key()
        self.cipher = Fernet(self.master_key)
    
    def _load_or_generate_master_key(self):
        """Load existing master key or generate a new one"""
        key_file_path = "master.key"
        
        try:
            if os.path.exists(key_file_path):
                with open(key_file_path, "rb") as key_file:
                    key = key_file.read()
                    logger.info("Loaded existing master key")
                    return key
            else:
                # Generate new key
                key = Fernet.generate_key()
                with open(key_file_path, "wb") as key_file:
                    key_file.write(key)
                logger.info("Generated new master key")
                return key
        except Exception as e:
            logger.error(f"Error handling master key: {e}")
            # Fallback to environment variable or generate temporary key
            env_key = os.getenv("MASTER_ENCRYPTION_KEY")
            if env_key:
                return base64.urlsafe_b64encode(env_key.encode()[:32].ljust(32, b'\0'))
            else:
                logger.warning("Using temporary key - messages will not persist between restarts")
                return Fernet.generate_key()
    
    def encrypt_message(self, message_text):
        """Encrypt a message using Fernet cipher"""
        try:
            if not isinstance(message_text, str):
                raise ValueError("Message must be a string")
            
            # Encode message to bytes and encrypt
            message_bytes = message_text.encode('utf-8')
            encrypted_bytes = self.cipher.encrypt(message_bytes)
            
            # Return base64 encoded string for database storage
            encrypted_string = base64.urlsafe_b64encode(encrypted_bytes).decode('utf-8')
            logger.debug(f"Successfully encrypted message of length {len(message_text)}")
            
            return encrypted_string
            
        except Exception as e:
            logger.error(f"Error encrypting message: {e}")
            raise CryptoError(f"Failed to encrypt message: {str(e)}")
    
    def decrypt_message(self, encrypted_message):
        """Decrypt a message using Fernet cipher"""
        try:
            if not encrypted_message:
                raise ValueError("Encrypted message cannot be empty")
            
            # Decode from base64 and decrypt
            encrypted_bytes = base64.urlsafe_b64decode(encrypted_message.encode('utf-8'))
            decrypted_bytes = self.cipher.decrypt(encrypted_bytes)
            
            # Decode to string
            message_text = decrypted_bytes.decode('utf-8')
            logger.debug(f"Successfully decrypted message of length {len(message_text)}")
            
            return message_text
            
        except Exception as e:
            logger.error(f"Error decrypting message: {e}")
            raise CryptoError(f"Failed to decrypt message: {str(e)}")
    
    def generate_room_key(self, room_id, user_id):
        """Generate a deterministic key for room-specific encryption (if needed)"""
        try:
            # Create a deterministic key based on room and user
            salt = f"room_{room_id}_user_{user_id}".encode('utf-8')
            kdf = PBKDF2HMAC(
                algorithm=hashes.SHA256(),
                length=32,
                salt=salt,
                iterations=100000,
            )
            key = base64.urlsafe_b64encode(kdf.derive(self.master_key))
            return key
        except Exception as e:
            logger.error(f"Error generating room key: {e}")
            raise CryptoError(f"Failed to generate room key: {str(e)}")

class CryptoError(Exception):
    """Custom exception for cryptography-related errors"""
    pass

# Global crypto manager instance
crypto_manager = CryptoManager()
