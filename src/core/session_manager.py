import os
import json
from cryptography.fernet import Fernet
from typing import Optional, Dict
from src.utils.logger import setup_logger

logger = setup_logger(__name__)

class SessionManager:
    def __init__(self, session_dir: str, encryption_key: Optional[str] = None):
        self.session_dir = session_dir
        self.encryption_key = encryption_key or Fernet.generate_key()
        self.cipher_suite = Fernet(self.encryption_key)
        
        # Create session directory if it doesn't exist
        os.makedirs(session_dir, exist_ok=True)
        
    def save_session(self, username: str, session_data: Dict) -> bool:
        """
        Сохраняет зашифрованные данные сессии
        """
        try:
            # Convert session data to JSON
            json_data = json.dumps(session_data)
            
            # Encrypt data
            encrypted_data = self.cipher_suite.encrypt(json_data.encode())
            
            # Save to file
            session_file = os.path.join(self.session_dir, f"{username}.session")
            with open(session_file, 'wb') as f:
                f.write(encrypted_data)
                
            return True
        except Exception as e:
            logger.error(f"Failed to save session for {username}: {e}")
            return False
            
    def load_session(self, username: str) -> Optional[Dict]:
        """
        Загружает и расшифровывает данные сессии
        """
        try:
            session_file = os.path.join(self.session_dir, f"{username}.session")
            
            if not os.path.exists(session_file):
                return None
                
            # Read encrypted data
            with open(session_file, 'rb') as f:
                encrypted_data = f.read()
                
            # Decrypt data
            decrypted_data = self.cipher_suite.decrypt(encrypted_data)
            
            # Parse JSON
            return json.loads(decrypted_data.decode())
        except Exception as e:
            logger.error(f"Failed to load session for {username}: {e}")
            return None
            
    def delete_session(self, username: str) -> bool:
        """
        Удаляет файл сессии
        """
        try:
            session_file = os.path.join(self.session_dir, f"{username}.session")
            
            if os.path.exists(session_file):
                os.remove(session_file)
                
            return True
        except Exception as e:
            logger.error(f"Failed to delete session for {username}: {e}")
            return False
            
    def list_sessions(self) -> list[str]:
        """
        Возвращает список всех сохраненных сессий
        """
        try:
            sessions = []
            for file in os.listdir(self.session_dir):
                if file.endswith('.session'):
                    sessions.append(file[:-8])  # Remove .session extension
            return sessions
        except Exception as e:
            logger.error(f"Failed to list sessions: {e}")
            return [] 