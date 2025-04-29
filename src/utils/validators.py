import re
from typing import Tuple, List
from urllib.parse import urlparse

def validate_telegram_link(link: str) -> Tuple[bool, str]:
    """
    Проверяет, является ли ссылка валидной для Telegram (принимает @, t.me/, http, https)
    """
    link = link.strip()
    if link.startswith('@') or link.startswith('t.me/') or link.startswith('https://t.me/') or link.startswith('http://t.me/') or link.startswith('http://') or link.startswith('https://'):
        return True, ""
    return False, "Невалидная ссылка"

def validate_links(links: List[str]) -> Tuple[List[str], List[str]]:
    """
    Валидирует список ссылок
    Возвращает (valid_links, invalid_links)
    """
    valid_links = []
    invalid_links = []
    
    for link in links:
        is_valid, _ = validate_telegram_link(link)
        if is_valid:
            valid_links.append(link)
        else:
            invalid_links.append(link)
            
    return valid_links, invalid_links 