from telethon import TelegramClient
from telethon.tl.functions.channels import JoinChannelRequest
from telethon.tl.functions.messages import ImportChatInviteRequest
from telethon.errors import (
    ChatAdminRequiredError,
    ChannelPrivateError,
    InviteHashExpiredError,
    UserAlreadyParticipantError,
    FloodWaitError
)
import re
from typing import Optional, Tuple
import asyncio
from datetime import datetime

from config.config import settings
from src.database.models import Account, Link, JoinAttempt
from src.utils.logger import setup_logger

logger = setup_logger(__name__)

class AccountManager:
    def __init__(self, session_file: str):
        self.client = TelegramClient(
            session_file,
            settings.API_ID,
            settings.API_HASH,
            proxy=self._get_proxy_settings()
        )
        self.current_delay = settings.MIN_JOIN_DELAY
        
    def _get_proxy_settings(self):
        if not settings.USE_PROXY:
            return None
            
        return {
            'proxy_type': settings.PROXY_TYPE,
            'addr': settings.PROXY_HOST,
            'port': settings.PROXY_PORT,
            'username': settings.PROXY_USERNAME,
            'password': settings.PROXY_PASSWORD
        }
        
    async def connect(self) -> bool:
        try:
            await self.client.connect()
            return await self.client.is_user_authorized()
        except Exception as e:
            logger.error(f"Failed to connect: {e}")
            return False
            
    async def get_account_info(self) -> Tuple[bool, str, int, int]:
        try:
            me = await self.client.get_me()
            full = await self.client.get_entity(me.id)
            
            # Get account type
            account_type = "free"
            if hasattr(full, 'premium'):
                account_type = "premium"
            elif hasattr(full, 'business'):
                account_type = "business"
                
            # Get groups count and limit
            dialogs = await self.client.get_dialogs()
            groups_count = len([d for d in dialogs if d.is_group or d.is_channel])
            
            # Approximate limit based on account type
            groups_limit = 500 if account_type == "free" else 2000
            
            return True, account_type, groups_count, groups_limit
        except Exception as e:
            logger.error(f"Failed to get account info: {e}")
            return False, "unknown", 0, 0
            
    async def join_chat(self, url: str) -> Tuple[bool, str]:
        try:
            # Extract username or invite hash
            if 't.me/' in url:
                username = url.split('t.me/')[-1]
            elif url.startswith('@'):
                username = url[1:]
            else:
                username = url
                
            # Try to join
            if '+' in username or len(username) > 5:  # Likely an invite link
                invite_hash = username.split('+')[-1]
                await self.client(ImportChatInviteRequest(invite_hash))
            else:
                await self.client(JoinChannelRequest(username))
                
            # Update delay
            self.current_delay = min(
                self.current_delay * (1 + settings.DELAY_INCREMENT),
                settings.MAX_JOIN_DELAY
            )
            
            return True, ""
        except UserAlreadyParticipantError:
            return True, "Already a member"
        except FloodWaitError as e:
            wait_time = e.seconds
            self.current_delay = max(wait_time, self.current_delay)
            return False, f"Flood wait: {wait_time} seconds"
        except (ChatAdminRequiredError, ChannelPrivateError, InviteHashExpiredError) as e:
            return False, str(e)
        except Exception as e:
            logger.error(f"Failed to join chat {url}: {e}")
            return False, str(e)
            
    async def process_links(self, links: list[Link], progress_callback=None) -> Tuple[int, int]:
        success_count = 0
        fail_count = 0
        
        for link in links:
            if progress_callback:
                await progress_callback(success_count, fail_count, len(links))
                
            success, error = await self.join_chat(link.url)
            
            if success:
                success_count += 1
                link.status = "success"
            else:
                fail_count += 1
                link.status = "failed"
                
            # Create join attempt record
            join_attempt = JoinAttempt(
                account_id=link.account_id,
                link_id=link.id,
                status="success" if success else "failed",
                error_message=error
            )
            
            # Wait before next join
            await asyncio.sleep(self.current_delay)
            
        return success_count, fail_count 