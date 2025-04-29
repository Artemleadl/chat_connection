from aiogram import Router, F
from aiogram.types import Message, CallbackQuery
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from typing import Optional

from src.database.models import Account, Link
from src.core import AccountManager
from src.utils.keyboard import (
    get_accounts_keyboard,
    get_main_menu_keyboard,
    get_links_keyboard
)
from src.utils.messages import (
    get_welcome_message,
    get_account_info_message,
    get_links_status_message
)
from src.utils.logger import setup_logger

logger = setup_logger(__name__)

router = Router()

class AccountStates(StatesGroup):
    waiting_for_phone = State()
    waiting_for_code = State()
    waiting_for_password = State()

class LinkStates(StatesGroup):
    waiting_for_links = State()

@router.message(Command("start"))
async def cmd_start(message: Message):
    await message.answer(
        get_welcome_message(),
        reply_markup=get_main_menu_keyboard()
    )

@router.message(Command("accounts"))
async def cmd_accounts(message: Message):
    accounts = await Account.get_all()
    if not accounts:
        await message.answer(
            "У вас пока нет добавленных аккаунтов. Используйте /add_account для добавления."
        )
        return
        
    keyboard = get_accounts_keyboard(accounts)
    await message.answer(
        "Выберите аккаунт для управления:",
        reply_markup=keyboard
    )

@router.message(Command("add_account"))
async def cmd_add_account(message: Message, state: FSMContext):
    await state.set_state(AccountStates.waiting_for_phone)
    await message.answer(
        "Пожалуйста, отправьте номер телефона в международном формате (например, +79123456789):"
    )

@router.message(AccountStates.waiting_for_phone)
async def process_phone(message: Message, state: FSMContext):
    phone = message.text.strip()
    if not phone.startswith('+'):
        await message.answer("Пожалуйста, отправьте номер в международном формате, начиная с '+'")
        return
        
    await state.update_data(phone=phone)
    await state.set_state(AccountStates.waiting_for_code)
    
    # Создаем менеджер аккаунта
    account_manager = AccountManager(f"sessions/{phone}")
    if not await account_manager.connect():
        await message.answer(
            "Ошибка при подключении к Telegram. Попробуйте позже."
        )
        await state.clear()
        return
        
    await message.answer(
        "Код подтверждения отправлен в Telegram. Пожалуйста, введите его:"
    )

@router.message(AccountStates.waiting_for_code)
async def process_code(message: Message, state: FSMContext):
    code = message.text.strip()
    data = await state.get_data()
    phone = data['phone']
    
    account_manager = AccountManager(f"sessions/{phone}")
    try:
        # Здесь должна быть логика проверки кода
        # После успешной авторизации:
        account = await Account.create(phone=phone)
        await message.answer(
            f"Аккаунт {phone} успешно добавлен!",
            reply_markup=get_main_menu_keyboard()
        )
    except Exception as e:
        logger.error(f"Failed to verify code: {e}")
        await message.answer(
            "Ошибка при проверке кода. Попробуйте добавить аккаунт снова."
        )
    
    await state.clear()

@router.message(Command("links"))
async def cmd_links(message: Message):
    links = await Link.get_all()
    if not links:
        await message.answer(
            "У вас пока нет добавленных ссылок. Используйте /add_links для добавления."
        )
        return
        
    keyboard = get_links_keyboard(links)
    await message.answer(
        "Выберите действие со ссылками:",
        reply_markup=keyboard
    )

@router.message(Command("add_links"))
async def cmd_add_links(message: Message, state: FSMContext):
    await state.set_state(LinkStates.waiting_for_links)
    await message.answer(
        "Пожалуйста, отправьте ссылки на чаты, по одной ссылке на строку:"
    )

@router.message(LinkStates.waiting_for_links)
async def process_links(message: Message, state: FSMContext):
    links = [link.strip() for link in message.text.split('\n') if link.strip()]
    if not links:
        await message.answer("Не найдено ни одной ссылки. Попробуйте еще раз.")
        return
        
    # Здесь должна быть валидация ссылок
    for link in links:
        await Link.create(url=link)
        
    await message.answer(
        f"Успешно добавлено {len(links)} ссылок!",
        reply_markup=get_main_menu_keyboard()
    )
    await state.clear()

@router.callback_query(F.data.startswith("account_"))
async def process_account_callback(callback: CallbackQuery):
    account_id = int(callback.data.split("_")[1])
    account = await Account.get(account_id)
    if not account:
        await callback.answer("Аккаунт не найден")
        return
        
    account_manager = AccountManager(f"sessions/{account.phone}")
    if not await account_manager.connect():
        await callback.answer("Ошибка при подключении к аккаунту")
        return
        
    success, account_type, groups_count, groups_limit = await account_manager.get_account_info()
    if not success:
        await callback.answer("Ошибка при получении информации об аккаунте")
        return
        
    await callback.message.edit_text(
        get_account_info_message(account, account_type, groups_count, groups_limit),
        reply_markup=get_accounts_keyboard(await Account.get_all())
    )

@router.callback_query(F.data.startswith("links_"))
async def process_links_callback(callback: CallbackQuery):
    action = callback.data.split("_")[1]
    links = await Link.get_all()
    
    if action == "start":
        # Здесь должна быть логика запуска процесса присоединения
        await callback.answer("Процесс присоединения запущен")
    elif action == "stop":
        # Здесь должна быть логика остановки процесса
        await callback.answer("Процесс присоединения остановлен")
    elif action == "status":
        status_message = get_links_status_message(links)
        await callback.message.edit_text(
            status_message,
            reply_markup=get_links_keyboard(links)
        ) 