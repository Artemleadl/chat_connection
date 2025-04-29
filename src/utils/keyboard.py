from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from typing import List

from src.database.models import Account, Link

def get_main_menu_keyboard() -> InlineKeyboardMarkup:
    """Создает основное меню бота"""
    keyboard = [
        [
            InlineKeyboardButton(text="📱 Аккаунты", callback_data="menu_accounts"),
            InlineKeyboardButton(text="🔗 Ссылки", callback_data="menu_links")
        ],
        [
            InlineKeyboardButton(text="📊 Статистика", callback_data="menu_stats"),
            InlineKeyboardButton(text="⚙️ Настройки", callback_data="menu_settings")
        ]
    ]
    return InlineKeyboardMarkup(inline_keyboard=keyboard)

def get_accounts_keyboard(accounts: List[Account]) -> InlineKeyboardMarkup:
    """Создает клавиатуру для управления аккаунтами"""
    keyboard = []
    
    # Кнопки для каждого аккаунта
    for account in accounts:
        keyboard.append([
            InlineKeyboardButton(
                text=f"📱 {account.phone}",
                callback_data=f"account_{account.id}"
            )
        ])
    
    # Кнопки управления
    keyboard.append([
        InlineKeyboardButton(text="➕ Добавить", callback_data="account_add"),
        InlineKeyboardButton(text="🔄 Обновить", callback_data="account_refresh")
    ])
    
    # Кнопка возврата в главное меню
    keyboard.append([
        InlineKeyboardButton(text="◀️ Назад", callback_data="menu_main")
    ])
    
    return InlineKeyboardMarkup(inline_keyboard=keyboard)

def get_links_keyboard(links: List[Link]) -> InlineKeyboardMarkup:
    """Создает клавиатуру для управления ссылками"""
    keyboard = []
    
    # Кнопки управления процессом
    keyboard.append([
        InlineKeyboardButton(text="▶️ Старт", callback_data="links_start"),
        InlineKeyboardButton(text="⏹ Стоп", callback_data="links_stop")
    ])
    
    keyboard.append([
        InlineKeyboardButton(text="🔄 Статус", callback_data="links_status"),
        InlineKeyboardButton(text="➕ Добавить", callback_data="links_add")
    ])
    
    # Список ссылок
    for link in links:
        status_emoji = "✅" if link.is_joined else "❌"
        keyboard.append([
            InlineKeyboardButton(
                text=f"{status_emoji} {link.url}",
                callback_data=f"link_{link.id}"
            )
        ])
    
    # Кнопка возврата в главное меню
    keyboard.append([
        InlineKeyboardButton(text="◀️ Назад", callback_data="menu_main")
    ])
    
    return InlineKeyboardMarkup(inline_keyboard=keyboard)

def get_settings_keyboard() -> InlineKeyboardMarkup:
    """Создает клавиатуру настроек"""
    keyboard = [
        [
            InlineKeyboardButton(text="⏱ Задержки", callback_data="settings_delays"),
            InlineKeyboardButton(text="🔄 Лимиты", callback_data="settings_limits")
        ],
        [
            InlineKeyboardButton(text="🔔 Уведомления", callback_data="settings_notifications"),
            InlineKeyboardButton(text="📝 Логи", callback_data="settings_logs")
        ],
        [
            InlineKeyboardButton(text="◀️ Назад", callback_data="menu_main")
        ]
    ]
    return InlineKeyboardMarkup(inline_keyboard=keyboard)

def get_stats_keyboard() -> InlineKeyboardMarkup:
    """Создает клавиатуру статистики"""
    keyboard = [
        [
            InlineKeyboardButton(text="📊 Общая", callback_data="stats_general"),
            InlineKeyboardButton(text="📈 График", callback_data="stats_graph")
        ],
        [
            InlineKeyboardButton(text="📋 Отчет", callback_data="stats_report"),
            InlineKeyboardButton(text="🔄 Обновить", callback_data="stats_refresh")
        ],
        [
            InlineKeyboardButton(text="◀️ Назад", callback_data="menu_main")
        ]
    ]
    return InlineKeyboardMarkup(inline_keyboard=keyboard) 