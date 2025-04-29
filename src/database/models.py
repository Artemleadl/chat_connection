from datetime import datetime
from sqlalchemy import Column, Integer, String, Boolean, DateTime, ForeignKey, Text
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship

Base = declarative_base()

class Account(Base):
    __tablename__ = "accounts"
    
    id = Column(Integer, primary_key=True)
    phone = Column(String, unique=True, nullable=False)
    session_file = Column(String, nullable=False)
    is_active = Column(Boolean, default=True)
    successful_joins = Column(Integer, default=0)
    errors = Column(Integer, default=0)
    last_used = Column(DateTime, default=datetime.now)
    created_at = Column(DateTime, default=datetime.now)
    
    links = relationship("Link", back_populates="account")
    join_attempts = relationship("JoinAttempt", back_populates="account")

    def __repr__(self):
        return f"<Account(phone='{self.phone}', active={self.is_active}, joins={self.successful_joins})>"

class Link(Base):
    __tablename__ = "links"
    
    id = Column(Integer, primary_key=True)
    url = Column(String, unique=True, nullable=False)
    is_active = Column(Boolean, default=True)
    is_joined = Column(Boolean, default=False)
    successful_joins = Column(Integer, default=0)
    last_check = Column(DateTime, default=datetime.now)
    created_at = Column(DateTime, default=datetime.now)
    account_id = Column(Integer, ForeignKey("accounts.id"))
    
    account = relationship("Account", back_populates="links")
    join_attempts = relationship("JoinAttempt", back_populates="link")

    def __repr__(self):
        return f"<Link(url='{self.url}', active={self.is_active}, joined={self.is_joined})>"

class JoinAttempt(Base):
    __tablename__ = "join_attempts"
    
    id = Column(Integer, primary_key=True)
    account_id = Column(Integer, ForeignKey("accounts.id"))
    link_id = Column(Integer, ForeignKey("links.id"))
    status = Column(String)  # success/failed
    error_message = Column(Text, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    account = relationship("Account", back_populates="join_attempts")
    link = relationship("Link", back_populates="join_attempts") 