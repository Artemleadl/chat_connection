import re
from typing import Tuple, List
from urllib.parse import urlparse

def validate_telegram_link(link: str) -> Tuple[bool, str]:
    """
    Валидирует ссылку на Telegram чат/канал
    Возвращает (is_valid, error_message)
    """
    # Удаляем пробелы
    link = link.strip()
    
    # Проверяем формат @username
    if link.startswith('@'):
        username = link[1:]
        if re.match(r'^[a-zA-Z0-9_]{5,32}$', username):
            return True, ""
        return False, "Неверный формат username"
        
    # Проверяем формат t.me ссылки
    if 't.me/' in link:
        try:
            parsed = urlparse(link)
            if parsed.netloc == 't.me':
                path = parsed.path.strip('/')
                if path:
                    return True, ""
        except:
            pass
        return False, "Неверный формат t.me ссылки"
        
    # Проверяем формат invite ссылки
    if '+' in link:
        invite_hash = link.split('+')[-1]
        if re.match(r'^[a-zA-Z0-9_-]{10,}$', invite_hash):
            return True, ""
        return False, "Неверный формат invite ссылки"
        
    return False, "Неверный формат ссылки"

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