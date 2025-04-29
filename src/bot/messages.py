from typing import List

def get_welcome_message() -> str:
    return (
        "Добро пожаловать в Chat Connector!\n\n"
        "Этот бот поможет вам автоматически вступать в чаты Telegram.\n\n"
        "Выберите действие в меню ниже:"
    )

def get_account_add_message() -> str:
    return (
        "Пожалуйста, отправьте username аккаунта в формате @username\n\n"
        "Например: @example"
    )

def get_account_info_message(account_type: str, groups_count: int, groups_limit: int) -> str:
    return (
        f"Информация об аккаунте:\n\n"
        f"Тип: {account_type}\n"
        f"Группы: {groups_count}/{groups_limit}\n\n"
        f"Выберите действие:"
    )

def get_links_add_message() -> str:
    return (
        "Отправьте ссылки на группы/чаты (по одной в строке).\n\n"
        "Поддерживаемые форматы:\n"
        "- @username\n"
        "- t.me/username\n"
        "- https://t.me/username\n"
        "- t.me/+invitecode"
    )

def get_links_added_message(count: int) -> str:
    return (
        f"Добавлено {count} ссылок.\n\n"
        "Нажмите 'Начать вступление' чтобы начать процесс."
    )

def get_joining_start_message() -> str:
    return (
        "Начинаем процесс вступления...\n\n"
        "Успешно: 0/0\n"
        "Не удалось: 0"
    )

def get_joining_progress_message(success: int, failed: int, total: int) -> str:
    return (
        f"Процесс вступления...\n\n"
        f"Успешно: {success}/{total}\n"
        f"Не удалось: {failed}"
    )

def get_joining_complete_message(success: int, failed: int, total: int) -> str:
    return (
        f"Процесс вступления завершен!\n\n"
        f"Успешно: {success}/{total}\n"
        f"Не удалось: {failed}\n\n"
        "Нажмите 'Показать ошибки' чтобы увидеть детали."
    )

def get_failed_links_message(links: List[str]) -> str:
    if not links:
        return "Нет ссылок с ошибками."
        
    message = "Ссылки, в которые не удалось вступить:\n\n"
    for i, link in enumerate(links, 1):
        message += f"{i}. {link}\n"
    return message

def get_error_message(error: str) -> str:
    return f"Произошла ошибка: {error}\n\nПожалуйста, попробуйте еще раз."

def get_cancelled_message() -> str:
    return "Процесс вступления отменен."

def get_confirmation_message(action: str) -> str:
    messages = {
        "delete_account": "Вы уверены, что хотите удалить этот аккаунт?",
        "start_joining": "Вы уверены, что хотите начать процесс вступления?",
        "cancel_joining": "Вы уверены, что хотите отменить процесс вступления?"
    }
    return messages.get(action, "Вы уверены?") 