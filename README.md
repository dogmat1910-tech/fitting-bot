# 👗 Fitting Bot — Telegram-примерочная

Минимальный MVP: пользователь присылает альбом из 2 фото (себя + вещь), бот возвращает результат виртуальной примерки через [FASHN AI](https://fashn.ai/).

## Стек

- Python 3.10+
- [aiogram 3](https://docs.aiogram.dev/) — Telegram-бот
- [httpx](https://www.python-httpx.org/) — HTTP-клиент для FASHN API
- [FASHN AI](https://fashn.ai/) — виртуальная примерка (платный API с free trial)

Бот работает на **long polling** — публичный IP/домен не нужен. Запускается прямо на ноуте.

## Быстрый старт (macOS)

### 1. Клонируй репу

```bash
git clone https://github.com/dogmat1910-tech/fitting-bot.git
cd fitting-bot
```

### 2. Создай виртуальное окружение

```bash
python3 -m venv venv
```

```bash
source venv/bin/activate
```

### 3. Установи зависимости

```bash
pip install -r requirements.txt
```

### 4. Создай файл с токенами

```bash
cp .env.example .env
```

Открой `.env` в любом редакторе и вставь:
- `BOT_TOKEN` — токен от [@BotFather](https://t.me/BotFather)
- `FASHN_API_KEY` — ключ с https://app.fashn.ai/api

### 5. Запусти бота

```bash
python bot.py
```

В терминале появится `Bot starting...` — значит работает. Открой своего бота в Telegram, отправь `/start`, потом альбом из 2 фото.

## Как пользоваться

1. `/start` в чате с ботом
2. Прикрепи 2 фото **одним альбомом** (скрепка → выбери обе фотки):
   - 1-я: твоё фото в полный рост
   - 2-я: фото вещи (одежда, желательно на однотонном фоне)
3. Подожди 20–40 секунд → получи результат

## Архитектура

```
Telegram → aiogram (long polling) → FASHN /run → poll /status → отправка фото
```

Состояние не хранится: фотки берутся прямо по `file_id` из Telegram, FASHN качает их по URL.

## Что дальше (после MVP)

- 🗄 SQLite — сохранять гардероб юзера
- 👗 Сборка луков из сохранённого гардероба
- 💳 Монетизация (Telegram Stars / ЮKassa)
- 🚀 Деплой на VPS с pm2/systemd
