from typing import List, Optional, Dict, Any
from datetime import datetime, timedelta
from sqlalchemy import create_engine, and_, or_
from sqlalchemy.orm import sessionmaker
from sqlalchemy.exc import SQLAlchemyError

from src.database.models import Account, Link, Base
from src.config import settings

class DatabaseManager:
    def __init__(self):
        self.engine = create_engine(settings.DATABASE_URL)
        self.Session = sessionmaker(bind=self.engine)
        Base.metadata.create_all(self.engine)
        
    def add_account(self, phone: str) -> Optional[Account]:
        """Добавляет новый аккаунт"""
        try:
            session = self.Session()
            account = Account(phone=phone)
            session.add(account)
            session.commit()
            return account
        except SQLAlchemyError as e:
            print(f"Error adding account: {e}")
            session.rollback()
            return None
        finally:
            session.close()
            
    def get_account(self, phone: str) -> Optional[Account]:
        """Получает аккаунт по номеру телефона"""
        try:
            session = self.Session()
            return session.query(Account).filter(Account.phone == phone).first()
        except SQLAlchemyError as e:
            print(f"Error getting account: {e}")
            return None
        finally:
            session.close()
            
    def get_active_accounts(self) -> List[Account]:
        """Получает список активных аккаунтов"""
        try:
            session = self.Session()
            return session.query(Account).filter(
                Account.is_active == True,
                Account.errors < settings.MAX_ERRORS
            ).all()
        except SQLAlchemyError as e:
            print(f"Error getting active accounts: {e}")
            return []
        finally:
            session.close()
            
    def update_account_stats(self, account: Account, success: bool = True) -> bool:
        """Обновляет статистику аккаунта"""
        try:
            session = self.Session()
            db_account = session.query(Account).filter(Account.id == account.id).first()
            if not db_account:
                return False
                
            if success:
                db_account.successful_joins += 1
            else:
                db_account.errors += 1
                
            db_account.last_used = datetime.now()
            session.commit()
            return True
        except SQLAlchemyError as e:
            print(f"Error updating account stats: {e}")
            session.rollback()
            return False
        finally:
            session.close()
            
    def add_link(self, url: str) -> Optional[Link]:
        """Добавляет новую ссылку"""
        try:
            session = self.Session()
            link = Link(url=url)
            session.add(link)
            session.commit()
            return link
        except SQLAlchemyError as e:
            print(f"Error adding link: {e}")
            session.rollback()
            return None
        finally:
            session.close()
            
    def get_link(self, url: str) -> Optional[Link]:
        """Получает ссылку по URL"""
        try:
            session = self.Session()
            return session.query(Link).filter(Link.url == url).first()
        except SQLAlchemyError as e:
            print(f"Error getting link: {e}")
            return None
        finally:
            session.close()
            
    def get_active_links(self) -> List[Link]:
        """Получает список активных ссылок"""
        try:
            session = self.Session()
            return session.query(Link).filter(
                Link.is_active == True,
                Link.successful_joins < settings.MAX_JOINS_PER_LINK
            ).all()
        except SQLAlchemyError as e:
            print(f"Error getting active links: {e}")
            return []
        finally:
            session.close()
            
    def update_link_stats(self, link: Link, success: bool = True) -> bool:
        """Обновляет статистику ссылки"""
        try:
            session = self.Session()
            db_link = session.query(Link).filter(Link.id == link.id).first()
            if not db_link:
                return False
                
            if success:
                db_link.successful_joins += 1
                db_link.is_joined = True
                
            db_link.last_check = datetime.now()
            session.commit()
            return True
        except SQLAlchemyError as e:
            print(f"Error updating link stats: {e}")
            session.rollback()
            return False
        finally:
            session.close()
            
    def get_stats(self) -> Dict[str, Any]:
        """Получает общую статистику"""
        try:
            session = self.Session()
            accounts = session.query(Account).all()
            links = session.query(Link).all()
            
            return {
                "total_accounts": len(accounts),
                "active_accounts": len([a for a in accounts if a.is_active]),
                "total_links": len(links),
                "active_links": len([l for l in links if l.is_active]),
                "total_joins": sum(a.successful_joins for a in accounts),
                "total_errors": sum(a.errors for a in accounts)
            }
        except SQLAlchemyError as e:
            print(f"Error getting stats: {e}")
            return {}
        finally:
            session.close()
            
    def cleanup_inactive(self) -> None:
        """Очищает неактивные записи"""
        try:
            session = self.Session()
            # Очистка старых аккаунтов
            old_date = datetime.now() - timedelta(days=settings.ACCOUNT_CLEANUP_DAYS)
            session.query(Account).filter(
                and_(
                    Account.last_used < old_date,
                    Account.successful_joins == 0
                )
            ).delete()
            
            # Очистка старых ссылок
            old_date = datetime.now() - timedelta(days=settings.LINK_CLEANUP_DAYS)
            session.query(Link).filter(
                and_(
                    Link.last_check < old_date,
                    Link.successful_joins == 0
                )
            ).delete()
            
            session.commit()
        except SQLAlchemyError as e:
            print(f"Error cleaning up inactive records: {e}")
            session.rollback()
        finally:
            session.close() 