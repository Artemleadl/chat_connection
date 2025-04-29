from telegram import Update
from telegram.ext import ContextTypes
from typing import Dict, Optional
import asyncio

from src.core.account_manager import AccountManager
from src.core.session_manager import SessionManager
from src.database.operations import DatabaseOperations
from src.utils.validators import validate_links
from src.bot.keyboards import (
    get_main_menu,
    get_account_menu,
    get_joining_menu,
    get_confirmation_menu,
    get_error_details_menu
)
from src.bot.messages import (
    get_welcome_message,
    get_account_add_message,
    get_account_info_message,
    get_links_add_message,
    get_links_added_message,
    get_joining_start_message,
    get_joining_progress_message,
    get_joining_complete_message,
    get_failed_links_message,
    get_error_message,
    get_cancelled_message,
    get_confirmation_message
)
from src.utils.logger import setup_logger

logger = setup_logger(__name__)

class BotHandlers:
    def __init__(self, db_ops: DatabaseOperations, session_manager: SessionManager):
        self.db_ops = db_ops
        self.session_manager = session_manager
        self.active_accounts: Dict[int, AccountManager] = {}
        self.active_join_tasks: Dict[int, asyncio.Task] = {}
        
    async def start(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """
        Обработчик команды /start
        """
        logger.info(f"/start received from user {update.effective_user.id}")
        context.user_data.clear()
        await update.message.reply_text(
            get_welcome_message(),
            reply_markup=get_main_menu()
        )
        
    async def add_account(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """
        Обработчик добавления аккаунта (теперь по номеру телефона)
        """
        await update.callback_query.message.reply_text(
            "Пожалуйста, отправьте номер телефона в международном формате (например, +79991234567)"
        )
        context.user_data["state"] = "waiting_for_phone"

    async def handle_account_input(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """
        Обработчик ввода номера телефона и кода подтверждения
        """
        state = context.user_data.get("state")
        text = update.message.text.strip()

        if state == "waiting_for_phone":
            if not text.startswith("+") or not text[1:].isdigit():
                await update.message.reply_text(
                    "Пожалуйста, отправьте номер телефона в международном формате, начиная с + и только цифры."
                )
                return
            context.user_data["phone"] = text
            context.user_data["state"] = "waiting_for_code"
            # Создаем менеджер аккаунта
            session_file = f"sessions/{text}.session"
            account_manager = AccountManager(session_file)
            context.user_data["account_manager"] = account_manager
            try:
                await account_manager.client.connect()
                if not await account_manager.client.is_user_authorized():
                    await account_manager.client.send_code_request(text)
                    await update.message.reply_text(
                        "Код подтверждения отправлен в Telegram. Пожалуйста, введите его:"
                    )
                else:
                    # Всегда сохраняем аккаунт в базу, даже если уже авторизован
                    account = self.db_ops.get_account(text)
                    if not account:
                        account = self.db_ops.create_account(
                            phone=text,
                            session_file=f"sessions/{text}.session",
                            account_type="unknown",
                            groups_limit=0,
                            current_groups=0
                        )
                    self.active_accounts[update.effective_user.id] = account_manager
                    await update.message.reply_text(
                        "Аккаунт готов к работе. Выберите действие в меню.",
                        reply_markup=get_main_menu()
                    )
                    context.user_data["state"] = None
            except Exception as e:
                await update.message.reply_text(f"Ошибка при отправке кода: {e}")
                context.user_data["state"] = None
            return

        if state == "waiting_for_code":
            phone = context.user_data.get("phone")
            account_manager = context.user_data.get("account_manager")
            code = text
            try:
                await account_manager.client.sign_in(phone, code)
                # Получаем инфо об аккаунте
                success, account_type, groups_count, groups_limit = await account_manager.get_account_info()
                if success:
                    account = self.db_ops.create_account(
                        phone=phone,
                        session_file=f"sessions/{phone}.session",
                        account_type=account_type,
                        groups_limit=groups_limit,
                        current_groups=groups_count
                    )
                    if account:
                        self.active_accounts[update.effective_user.id] = account_manager
                        await update.message.reply_text(
                            get_account_info_message(account_type, groups_count, groups_limit),
                            reply_markup=get_account_menu()
                        )
                    else:
                        await update.message.reply_text(
                            get_error_message("Не удалось сохранить аккаунт в базе данных")
                        )
                else:
                    await update.message.reply_text(
                        get_error_message("Не удалось получить информацию об аккаунте")
                    )
            except Exception as e:
                await update.message.reply_text(f"Ошибка авторизации: {e}")
            context.user_data["state"] = None
            return

        # Если не в процессе добавления аккаунта, игнорируем
        return
        
    async def check_account(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """
        Обработчик проверки аккаунта
        """
        phone = context.user_data.get("phone")
        if not phone and update.effective_user.id in self.active_accounts:
            account_manager = self.active_accounts[update.effective_user.id]
            phone = account_manager.client.session.filename.split("/")[-1].replace(".session", "")
        if not phone:
            await update.callback_query.message.reply_text(
                get_error_message("Сначала добавьте аккаунт")
            )
            return
        account_manager = self.active_accounts.get(update.effective_user.id)
        if not account_manager:
            await update.callback_query.message.reply_text(
                get_error_message("Сначала добавьте аккаунт")
            )
            return
        success, account_type, groups_count, groups_limit = await account_manager.get_account_info()
        if success:
            await update.callback_query.message.reply_text(
                get_account_info_message(account_type, groups_count, groups_limit),
                reply_markup=get_account_menu()
            )
        else:
            await update.callback_query.message.reply_text(
                get_error_message("Не удалось получить информацию об аккаунте")
            )
            
    async def add_links(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """
        Обработчик добавления ссылок
        """
        if update.effective_user.id not in self.active_accounts:
            await update.callback_query.message.reply_text(
                get_error_message("Сначала добавьте аккаунт")
            )
            return
            
        await update.callback_query.message.reply_text(
            get_links_add_message()
        )
        context.user_data["state"] = "waiting_for_links"
        
    async def handle_links_input(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """
        Обработчик ввода ссылок
        """
        if context.user_data.get("state") != "waiting_for_links":
            return
        links = update.message.text.strip().split("\n")
        valid_links, invalid_links = validate_links(links)
        if not valid_links:
            await update.message.reply_text(
                get_error_message("Не найдено валидных ссылок")
            )
            return
        # Get account
        phone = context.user_data.get("phone")
        if not phone and update.effective_user.id in self.active_accounts:
            # Вытаскиваем phone из сессии аккаунта
            account_manager = self.active_accounts[update.effective_user.id]
            phone = account_manager.client.session.filename.split("/")[-1].replace(".session", "")
        account = self.db_ops.get_account(phone)
        if not account:
            await update.message.reply_text(
                get_error_message("Аккаунт не найден в базе данных")
            )
            return
        # Save links
        saved_links = self.db_ops.add_links(account.id, valid_links)
        if saved_links:
            await update.message.reply_text(
                get_links_added_message(len(saved_links)),
                reply_markup=get_main_menu()
            )
        else:
            await update.message.reply_text(
                get_error_message("Не удалось сохранить ссылки")
            )
        context.user_data["state"] = None
        
    async def start_joining(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """
        Обработчик начала процесса вступления
        """
        phone = context.user_data.get("phone")
        if not phone and update.effective_user.id in self.active_accounts:
            account_manager = self.active_accounts[update.effective_user.id]
            phone = account_manager.client.session.filename.split("/")[-1].replace(".session", "")
        if not phone:
            await update.callback_query.message.reply_text(
                get_error_message("Сначала добавьте аккаунт")
            )
            return
        account = self.db_ops.get_account(phone)
        if not account:
            await update.callback_query.message.reply_text(
                get_error_message("Аккаунт не найден в базе данных")
            )
            return
        links = self.db_ops.get_pending_links(account.id)
        if not links:
            await update.callback_query.message.reply_text(
                get_error_message("Нет ссылок для вступления")
            )
            return
        progress_message = await update.callback_query.message.reply_text(
            get_joining_start_message(),
            reply_markup=get_joining_menu()
        )
        account_manager = self.active_accounts[update.effective_user.id]
        async def progress_callback(success: int, failed: int, total: int):
            await progress_message.edit_text(
                get_joining_progress_message(success, failed, total),
                reply_markup=get_joining_menu()
            )
        task = asyncio.create_task(
            account_manager.process_links(links, progress_callback)
        )
        self.active_join_tasks[update.effective_user.id] = task
        
    async def cancel_joining(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """
        Обработчик отмены процесса вступления
        """
        if update.effective_user.id in self.active_join_tasks:
            task = self.active_join_tasks[update.effective_user.id]
            task.cancel()
            del self.active_join_tasks[update.effective_user.id]
            
            await update.callback_query.message.edit_text(
                get_cancelled_message(),
                reply_markup=get_main_menu()
            )
            
    async def show_errors(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """
        Обработчик показа ошибок
        """
        phone = context.user_data.get("phone")
        if not phone and update.effective_user.id in self.active_accounts:
            account_manager = self.active_accounts[update.effective_user.id]
            phone = account_manager.client.session.filename.split("/")[-1].replace(".session", "")
        if not phone:
            await update.callback_query.message.reply_text(
                get_error_message("Сначала добавьте аккаунт")
            )
            return
        account = self.db_ops.get_account(phone)
        if not account:
            await update.callback_query.message.reply_text(
                get_error_message("Аккаунт не найден в базе данных")
            )
            return
        failed_links = self.db_ops.get_failed_links(account.id)
        await update.callback_query.message.reply_text(
            get_failed_links_message([link.url for link in failed_links]),
            reply_markup=get_error_details_menu()
        )

    async def main_menu(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """
        Обработчик возврата в главное меню по кнопке 'Назад'
        """
        await update.callback_query.message.edit_text(
            get_welcome_message(),
            reply_markup=get_main_menu()
        ) 