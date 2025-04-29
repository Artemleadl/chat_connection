from telegram import InlineKeyboardButton, InlineKeyboardMarkup

def get_main_menu() -> InlineKeyboardMarkup:
    """
    Создает главное меню бота
    """
    keyboard = [
        [InlineKeyboardButton("Добавить аккаунт", callback_data="add_account")],
        [InlineKeyboardButton("Проверить аккаунт", callback_data="check_account")],
        [InlineKeyboardButton("Добавить ссылки", callback_data="add_links")],
        [InlineKeyboardButton("Начать вступление", callback_data="start_joining")]
    ]
    return InlineKeyboardMarkup(keyboard)

def get_account_menu() -> InlineKeyboardMarkup:
    """
    Создает меню управления аккаунтом
    """
    keyboard = [
        [InlineKeyboardButton("Проверить статус", callback_data="check_status")],
        [InlineKeyboardButton("Удалить аккаунт", callback_data="delete_account")],
        [InlineKeyboardButton("Назад", callback_data="main_menu")]
    ]
    return InlineKeyboardMarkup(keyboard)

def get_joining_menu() -> InlineKeyboardMarkup:
    """
    Создает меню процесса вступления
    """
    keyboard = [
        [InlineKeyboardButton("Отменить", callback_data="cancel_joining")],
        [InlineKeyboardButton("Показать ошибки", callback_data="show_errors")]
    ]
    return InlineKeyboardMarkup(keyboard)

def get_confirmation_menu(action: str) -> InlineKeyboardMarkup:
    """
    Создает меню подтверждения действия
    """
    keyboard = [
        [
            InlineKeyboardButton("Да", callback_data=f"confirm_{action}"),
            InlineKeyboardButton("Нет", callback_data="cancel")
        ]
    ]
    return InlineKeyboardMarkup(keyboard)

def get_error_details_menu() -> InlineKeyboardMarkup:
    """
    Создает меню для просмотра деталей ошибок
    """
    keyboard = [
        [InlineKeyboardButton("Показать ссылки", callback_data="show_failed_links")],
        [InlineKeyboardButton("Показать причины", callback_data="show_error_reasons")],
        [InlineKeyboardButton("Назад", callback_data="main_menu")]
    ]
    return InlineKeyboardMarkup(keyboard) 