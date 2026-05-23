# 👗 Fitting Bot — Telegram-примерочная

Telegram-бот виртуальной примерки на **FASHN AI** API. Пользователь присылает альбом из 2 фото (себя + вещь), бот возвращает результат за 10–30 секунд.

## Стек

- Python 3.10+
- [aiogram 3](https://docs.aiogram.dev/) — Telegram-бот (long polling)
- [httpx](https://www.python-httpx.org/) — HTTP-клиент
- [FASHN AI](https://fashn.ai/) — try-on движок (~$0.04 за примерку, mode=quality)

Long polling — публичный IP/домен не нужен. Запускается локально на ноуте.

## Быстрый старт (macOS)

### 1. Клонируй репу

```bash
git clone https://github.com/dogmat1910-tech/fitting-bot.git
```

```bash
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

```bash
open -e .env
```

Вставь:
- `BOT_TOKEN` — токен от [@BotFather](https://t.me/BotFather)
- `FASHN_API_KEY` — ключ с https://app.fashn.ai/api

### 5. Запусти бота

```bash
python bot.py
```

Увидишь `Bot starting... model=tryon-v1.6 mode=quality` — значит работает.

## Как пользоваться

1. `/start` в чате с ботом
2. Прикрепи **2 фото одним альбомом**:
   - 1-я: фото в полный рост
   - 2-я: фото вещи (flat-lay лучше всего)
3. Опционально — **подпись к альбому**: «топ», «джинсы», «платье» и т.д. (бот сам определит, но точнее с подсказкой)
4. Подожди 10–30 секунд → готово

## Категории одежды

Бот автоматически определяет категорию по подписи (рус. + англ.):

| Категория | Ключевые слова |
|---|---|
| `tops` | топ, футболка, майка, рубашка, блузка, свитер, кофта, top, shirt, blouse |
| `bottoms` | джинсы, брюки, штаны, юбка, шорты, pants, jeans, skirt |
| `one-pieces` | платье, комбинезон, сарафан, dress, jumpsuit |
| `auto` | (без подписи или неизвестное слово) |

## Что дальше (после MVP)

- 🗄 SQLite — гардероб юзера (сохранить фото модели + вещи)
- 👗 Сборка луков из вещей в гардеробе
- 💳 Монетизация (Telegram Stars / ЮKassa)
- 🚀 Деплой на VPS с pm2

## История ветки

В git-истории есть версия на бесплатном Hugging Face IDM-VTON (commit `cdc947f` и ранее) — на случай если захочется вернуться на бесплатный движок для теста.
