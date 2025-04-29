# Telegram Chat Connector

Бот для автоматического вступления в чаты Telegram.

## Возможности

- Поддержка множества аккаунтов
- Автоматическое вступление в чаты
- Динамическая система пауз между вступлениями
- Детальная статистика и отчетность
- Поддержка различных форматов ссылок
- Отмена процесса вступления
- Проверка статуса аккаунта

## Установка

1. Клонируйте репозиторий:
```bash
git clone https://github.com/yourusername/chat_connector.git
cd chat_connector
```

2. Создайте файл .env на основе .env.example:
```bash
cp .env.example .env
```

3. Заполните необходимые параметры в .env:
- BOT_TOKEN - токен вашего бота от @BotFather
- API_ID и API_HASH - получите на https://my.telegram.org

4. Запустите с помощью Docker:
```bash
docker-compose up -d
```

## Использование

1. Запустите бота в Telegram
2. Нажмите "Добавить аккаунт" и отправьте username
3. После авторизации аккаунта добавьте ссылки на чаты
4. Нажмите "Начать вступление"

## Структура проекта

```
chat_connector/
├── docker/
│   ├── Dockerfile
│   └── docker-compose.yml
├── src/
│   ├── bot/
│   │   ├── handlers/
│   │   ├── keyboards/
│   │   └── messages/
│   ├── core/
│   │   ├── account_manager.py
│   │   ├── chat_joiner.py
│   │   └── session_manager.py
│   ├── database/
│   │   ├── models.py
│   │   └── operations.py
│   └── utils/
│       ├── logger.py
│       └── validators.py
├── tests/
├── logs/
├── sessions/
├── config/
├── requirements.txt
└── README.md
```

## Безопасность

- Сессии хранятся в зашифрованном виде
- Поддержка прокси для обхода ограничений
- Динамические паузы между вступлениями
- Обработка блокировок аккаунтов

## Лицензия

MIT 