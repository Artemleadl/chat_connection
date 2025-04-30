from sqlalchemy.orm import Session
from typing import List, Optional
from datetime import datetime

from src.database.models import Account, Link, JoinAttempt
from src.utils.logger import setup_logger

logger = setup_logger(__name__)

class DatabaseOperations:
    def __init__(self, db: Session):
        self.db = db
        
    def create_account(self, phone: str, session_file: str) -> Optional[Account]:
        """
        Создает новый аккаунт в базе данных
        """
        try:
            account = Account(
                phone=phone,
                session_file=session_file
            )
            
            self.db.add(account)
            self.db.commit()
            self.db.refresh(account)
            
            return account
        except Exception as e:
            logger.error(f"Failed to create account {phone}: {e}")
            self.db.rollback()
            return None
            
    def get_account(self, phone: str) -> Optional[Account]:
        """
        Получает аккаунт по phone
        """
        try:
            return self.db.query(Account).filter(Account.phone == phone).first()
        except Exception as e:
            logger.error(f"Failed to get account {phone}: {e}")
            return None
            
    def update_account_info(self, phone: str, groups_count: int) -> bool:
        """
        Обновляет информацию об аккаунте
        """
        try:
            account = self.get_account(phone)
            if account:
                account.current_groups = groups_count
                account.last_check = datetime.utcnow()
                self.db.commit()
                return True
            return False
        except Exception as e:
            logger.error(f"Failed to update account {phone}: {e}")
            self.db.rollback()
            return False
            
    def add_links(self, account_id: int, links: List[str]) -> List[Link]:
        """
        Добавляет ссылки для аккаунта
        """
        try:
            new_links = []
            for url in links:
                link = Link(
                    account_id=account_id,
                    url=url,
                    status="pending"
                )
                self.db.add(link)
                new_links.append(link)
                
            self.db.commit()
            return new_links
        except Exception as e:
            logger.error(f"Failed to add links for account {account_id}: {e}")
            self.db.rollback()
            return []
            
    def get_pending_links(self, account_id: int) -> List[Link]:
        """
        Получает список ожидающих ссылок для аккаунта
        """
        try:
            return self.db.query(Link).filter(
                Link.account_id == account_id,
                Link.status == "pending"
            ).all()
        except Exception as e:
            logger.error(f"Failed to get pending links for account {account_id}: {e}")
            return []
            
    def update_link_status(self, link_id: int, status: str, 
                          error_message: Optional[str] = None) -> bool:
        """
        Обновляет статус ссылки
        """
        try:
            link = self.db.query(Link).filter(Link.id == link_id).first()
            if link:
                link.status = status
                self.db.commit()
                return True
            return False
        except Exception as e:
            logger.error(f"Failed to update link {link_id}: {e}")
            self.db.rollback()
            return False
            
    def create_join_attempt(self, account_id: int, link_id: int, 
                          status: str, error_message: Optional[str] = None) -> Optional[JoinAttempt]:
        """
        Создает запись о попытке вступления
        """
        try:
            attempt = JoinAttempt(
                account_id=account_id,
                link_id=link_id,
                status=status,
                error_message=error_message
            )
            
            self.db.add(attempt)
            self.db.commit()
            self.db.refresh(attempt)
            
            return attempt
        except Exception as e:
            logger.error(f"Failed to create join attempt for link {link_id}: {e}")
            self.db.rollback()
            return None
            
    def get_failed_links(self, account_id: int) -> List[Link]:
        """
        Получает список ссылок, в которые не удалось вступить
        """
        try:
            return self.db.query(Link).filter(
                Link.account_id == account_id,
                Link.status == "failed"
            ).all()
        except Exception as e:
            logger.error(f"Failed to get failed links for account {account_id}: {e}")
            return [] 