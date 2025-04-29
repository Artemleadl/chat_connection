from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import (
    Application,
    CommandHandler,
    MessageHandler,
    CallbackQueryHandler,
    ContextTypes,
    filters
)
import asyncio
from typing import Dict, Optional
import os

from config.config import settings
from src.core.account_manager import AccountManager
from src.database.models import Account, Link, JoinAttempt
from src.utils.logger import setup_logger

logger = setup_logger(__name__)

class TelegramBot:
    def __init__(self):
        self.application = Application.builder().token(settings.BOT_TOKEN).build()
        self.active_accounts: Dict[int, AccountManager] = {}
        self.active_join_tasks: Dict[int, asyncio.Task] = {}
        
    async def start(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        keyboard = [
            [InlineKeyboardButton("Добавить аккаунт", callback_data="add_account")],
            [InlineKeyboardButton("Проверить аккаунт", callback_data="check_account")],
            [InlineKeyboardButton("Добавить ссылки", callback_data="add_links")],
            [InlineKeyboardButton("Начать вступление", callback_data="start_joining")]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        await update.message.reply_text(
            "Добро пожаловать! Выберите действие:",
            reply_markup=reply_markup
        )
        
    async def add_account(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        await update.callback_query.message.reply_text(
            "Пожалуйста, отправьте username аккаунта (например, @username)"
        )
        context.user_data["state"] = "waiting_for_account"
        
    async def handle_account_input(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        if context.user_data.get("state") != "waiting_for_account":
            return
            
        username = update.message.text.strip()
        if not username.startswith("@"):
            await update.message.reply_text(
                "Пожалуйста, отправьте username в формате @username"
            )
            return
            
        # Create account manager
        session_file = os.path.join(settings.SESSION_DIR, f"{username[1:]}.session")
        account_manager = AccountManager(session_file)
        
        # Try to connect
        if await account_manager.connect():
            # Get account info
            success, account_type, groups_count, groups_limit = await account_manager.get_account_info()
            
            if success:
                # Save to database
                account = Account(
                    username=username[1:],
                    session_file=session_file,
                    account_type=account_type,
                    groups_limit=groups_limit,
                    current_groups=groups_count
                )
                # TODO: Save to database
                
                self.active_accounts[update.effective_user.id] = account_manager
                
                await update.message.reply_text(
                    f"Аккаунт успешно добавлен!\n"
                    f"Тип: {account_type}\n"
                    f"Группы: {groups_count}/{groups_limit}"
                )
            else:
                await update.message.reply_text(
                    "Не удалось получить информацию об аккаунте"
                )
        else:
            await update.message.reply_text(
                "Не удалось подключиться к аккаунту. "
                "Пожалуйста, убедитесь, что сессия действительна."
            )
            
        context.user_data["state"] = None
        
    async def add_links(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        if update.effective_user.id not in self.active_accounts:
            await update.callback_query.message.reply_text(
                "Сначала добавьте аккаунт!"
            )
            return
            
        await update.callback_query.message.reply_text(
            "Отправьте ссылки на группы/чаты (по одной в строке):"
        )
        context.user_data["state"] = "waiting_for_links"
        
    async def handle_links_input(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        if context.user_data.get("state") != "waiting_for_links":
            return
            
        links = update.message.text.strip().split("\n")
        valid_links = []
        
        for link in links:
            link = link.strip()
            if any(link.startswith(prefix) for prefix in ["@", "t.me/", "http://", "https://"]):
                valid_links.append(link)
                
        if not valid_links:
            await update.message.reply_text(
                "Не найдено валидных ссылок. Попробуйте еще раз."
            )
            return
            
        # Save links to database
        # TODO: Save to database
        
        await update.message.reply_text(
            f"Добавлено {len(valid_links)} ссылок.\n"
            "Нажмите 'Начать вступление' чтобы начать процесс."
        )
        
        context.user_data["state"] = None
        
    async def start_joining(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        if update.effective_user.id not in self.active_accounts:
            await update.callback_query.message.reply_text(
                "Сначала добавьте аккаунт!"
            )
            return
            
        # Get links from database
        # TODO: Get from database
        links = []  # Placeholder
        
        if not links:
            await update.callback_query.message.reply_text(
                "Нет ссылок для вступления. Добавьте ссылки сначала."
            )
            return
            
        # Create progress message
        progress_message = await update.callback_query.message.reply_text(
            "Начинаем вступление...\n"
            "Успешно: 0/0\n"
            "Не удалось: 0"
        )
        
        # Start joining process
        account_manager = self.active_accounts[update.effective_user.id]
        
        async def progress_callback(success: int, failed: int, total: int):
            await progress_message.edit_text(
                f"Процесс вступления...\n"
                f"Успешно: {success}/{total}\n"
                f"Не удалось: {failed}"
            )
            
        # Create task
        task = asyncio.create_task(
            account_manager.process_links(links, progress_callback)
        )
        self.active_join_tasks[update.effective_user.id] = task
        
        # Add cancel button
        keyboard = [[InlineKeyboardButton("Отменить", callback_data="cancel_joining")]]
        await progress_message.edit_reply_markup(InlineKeyboardMarkup(keyboard))
        
    async def cancel_joining(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        if update.effective_user.id in self.active_join_tasks:
            task = self.active_join_tasks[update.effective_user.id]
            task.cancel()
            del self.active_join_tasks[update.effective_user.id]
            
            await update.callback_query.message.edit_text(
                "Процесс вступления отменен."
            )
            
    def setup_handlers(self):
        self.application.add_handler(CommandHandler("start", self.start))
        self.application.add_handler(CallbackQueryHandler(self.add_account, pattern="^add_account$"))
        self.application.add_handler(CallbackQueryHandler(self.add_links, pattern="^add_links$"))
        self.application.add_handler(CallbackQueryHandler(self.start_joining, pattern="^start_joining$"))
        self.application.add_handler(CallbackQueryHandler(self.cancel_joining, pattern="^cancel_joining$"))
        
        self.application.add_handler(MessageHandler(
            filters.TEXT & ~filters.COMMAND,
            self.handle_account_input
        ))
        
    def run(self):
        self.setup_handlers()
        self.application.run_polling() 