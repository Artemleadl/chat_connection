from typing import Optional, List, Dict, Any
import asyncio
from datetime import datetime, timedelta

from telethon import TelegramClient
from telethon.errors import (
    FloodWaitError,
    UserDeactivatedError,
    SessionPasswordNeededError,
    PhoneCodeInvalidError
)
from telethon.tl.functions.channels import JoinChannelRequest
from telegram import Update
from telegram.ext import ContextTypes

from src.database.models import Account, Link
from src.config import settings
from src.utils.messages import format_error_message, format_success_message

class TelegramManager:
    def __init__(self):
        self.clients: Dict[str, TelegramClient] = {}
        self.session_path = settings.SESSION_PATH
        
    async def create_client(self, account: Account) -> Optional[TelegramClient]:
        """Создает клиент для аккаунта"""
        try:
            client = TelegramClient(
                f"{self.session_path}/{account.phone}",
                settings.API_ID,
                settings.API_HASH
            )
            await client.connect()
            
            if not await client.is_user_authorized():
                await client.send_code_request(account.phone)
                return None
                
            self.clients[account.phone] = client
            return client
            
        except Exception as e:
            print(f"Error creating client for {account.phone}: {e}")
            return None
            
    async def join_channel(self, account: Account, link: Link) -> bool:
        """Присоединяет аккаунт к каналу"""
        try:
            client = self.clients.get(account.phone)
            if not client:
                client = await self.create_client(account)
                if not client:
                    return False
                    
            await client(JoinChannelRequest(link.url))
            
            # Обновляем статистику
            account.successful_joins += 1
            account.last_used = datetime.now()
            link.successful_joins += 1
            link.is_joined = True
            link.last_check = datetime.now()
            
            return True
            
        except FloodWaitError as e:
            # Обработка ограничений Telegram
            wait_time = e.seconds
            print(f"FloodWaitError for {account.phone}: {wait_time} seconds")
            await asyncio.sleep(wait_time)
            return False
            
        except Exception as e:
            print(f"Error joining channel for {account.phone}: {e}")
            account.errors += 1
            return False
            
    async def check_channel(self, account: Account, link: Link) -> bool:
        """Проверяет статус присоединения к каналу"""
        try:
            client = self.clients.get(account.phone)
            if not client:
                client = await self.create_client(account)
                if not client:
                    return False
                    
            entity = await client.get_entity(link.url)
            link.members_count = entity.participants_count
            link.last_check = datetime.now()
            
            return True
            
        except Exception as e:
            print(f"Error checking channel for {account.phone}: {e}")
            return False
            
    async def close_all(self):
        """Закрывает все клиенты"""
        for client in self.clients.values():
            await client.disconnect()
        self.clients.clear()

async def send_message(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE,
    text: str,
    reply_markup: Optional[Any] = None
) -> None:
    """Отправляет сообщение пользователю"""
    try:
        await context.bot.send_message(
            chat_id=update.effective_chat.id,
            text=text,
            reply_markup=reply_markup
        )
    except Exception as e:
        print(f"Error sending message: {e}")
        await context.bot.send_message(
            chat_id=update.effective_chat.id,
            text=format_error_message("Ошибка отправки сообщения")
        )

async def edit_message(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE,
    message_id: int,
    text: str,
    reply_markup: Optional[Any] = None
) -> None:
    """Редактирует существующее сообщение"""
    try:
        await context.bot.edit_message_text(
            chat_id=update.effective_chat.id,
            message_id=message_id,
            text=text,
            reply_markup=reply_markup
        )
    except Exception as e:
        print(f"Error editing message: {e}")
        await context.bot.send_message(
            chat_id=update.effective_chat.id,
            text=format_error_message("Ошибка редактирования сообщения")
        )

def get_user_info(update: Update) -> Dict[str, Any]:
    """Получает информацию о пользователе"""
    user = update.effective_user
    return {
        "id": user.id,
        "username": user.username,
        "first_name": user.first_name,
        "last_name": user.last_name,
        "language_code": user.language_code
    } 