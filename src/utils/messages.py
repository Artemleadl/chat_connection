from typing import List, Optional
from datetime import datetime

from src.database.models import Account, Link

def format_welcome_message() -> str:
    """Форматирует приветственное сообщение"""
    return (
        "👋 Добро пожаловать в бот для управления аккаунтами!\n\n"
        "🔹 Используйте /accounts для управления аккаунтами\n"
        "🔹 Используйте /links для управления ссылками\n"
        "🔹 Используйте /help для получения справки"
    )

def format_account_info(account: Account) -> str:
    """Форматирует информацию об аккаунте"""
    status = "✅ Активен" if account.is_active else "❌ Неактивен"
    last_used = account.last_used.strftime("%d.%m.%Y %H:%M") if account.last_used else "Никогда"
    
    return (
        f"📱 Аккаунт: {account.phone}\n"
        f"📊 Статус: {status}\n"
        f"🕒 Последнее использование: {last_used}\n"
        f"📈 Успешных присоединений: {account.successful_joins}\n"
        f"❌ Ошибок: {account.errors}"
    )

def format_link_info(link: Link) -> str:
    """Форматирует информацию о ссылке"""
    status = "✅ Присоединен" if link.is_joined else "❌ Не присоединен"
    last_check = link.last_check.strftime("%d.%m.%Y %H:%M") if link.last_check else "Никогда"
    
    return (
        f"🔗 Ссылка: {link.url}\n"
        f"📊 Статус: {status}\n"
        f"🕒 Последняя проверка: {last_check}\n"
        f"👥 Участников: {link.members_count}\n"
        f"📈 Успешных присоединений: {link.successful_joins}"
    )

def format_accounts_list(accounts: List[Account]) -> str:
    """Форматирует список аккаунтов"""
    if not accounts:
        return "❌ Нет добавленных аккаунтов"
    
    result = "📱 Список аккаунтов:\n\n"
    for i, account in enumerate(accounts, 1):
        status = "✅" if account.is_active else "❌"
        result += f"{i}. {status} {account.phone}\n"
    
    return result

def format_links_list(links: List[Link]) -> str:
    """Форматирует список ссылок"""
    if not links:
        return "❌ Нет добавленных ссылок"
    
    result = "🔗 Список ссылок:\n\n"
    for i, link in enumerate(links, 1):
        status = "✅" if link.is_joined else "❌"
        result += f"{i}. {status} {link.url}\n"
    
    return result

def format_error_message(error: str) -> str:
    """Форматирует сообщение об ошибке"""
    return f"❌ Ошибка: {error}"

def format_success_message(message: str) -> str:
    """Форматирует сообщение об успехе"""
    return f"✅ {message}"

def format_stats_message(
    total_accounts: int,
    active_accounts: int,
    total_links: int,
    joined_links: int,
    total_joins: int,
    successful_joins: int
) -> str:
    """Форматирует статистику"""
    return (
        "📊 Статистика:\n\n"
        f"📱 Аккаунты: {active_accounts}/{total_accounts} активны\n"
        f"🔗 Ссылки: {joined_links}/{total_links} присоединены\n"
        f"📈 Присоединения: {successful_joins}/{total_joins} успешных"
    )

def format_settings_message(
    delay_min: int,
    delay_max: int,
    max_joins_per_day: int,
    notifications_enabled: bool,
    logging_enabled: bool
) -> str:
    """Форматирует текущие настройки"""
    return (
        "⚙️ Текущие настройки:\n\n"
        f"⏱ Задержка между действиями: {delay_min}-{delay_max} сек\n"
        f"🔄 Максимум присоединений в день: {max_joins_per_day}\n"
        f"🔔 Уведомления: {'включены' if notifications_enabled else 'выключены'}\n"
        f"📝 Логирование: {'включено' if logging_enabled else 'выключено'}"
    ) 