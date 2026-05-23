# 👗 Fitting Bot — Telegram-примерочная

Минимальный MVP: пользователь присылает альбом из 2 фото (себя + вещь), бот возвращает результат виртуальной примерки.

**Бесплатный вариант** — использует публичный Hugging Face Space [yisol/IDM-VTON](https://huggingface.co/spaces/yisol/IDM-VTON) через `gradio_client`. Платить не нужно, но обработка занимает 1–3 минуты и Space иногда перегружен.

## Стек

- Python 3.10+
- [aiogram 3](https://docs.aiogram.dev/) — Telegram-бот (long polling)
- [gradio_client](https://www.gradio.app/docs/python-client/introduction) — вызов HF Space
- [IDM-VTON](https://huggingface.co/spaces/yisol/IDM-VTON) — open-source нейросеть для try-on

Бот работает на long polling — публичный IP/домен не нужен. Запускается на ноуте, на сервере, где угодно с интернетом.

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

Открой `.env`:

```bash
open -e .env
```

Вставь:
- `BOT_TOKEN` — токен от [@BotFather](https://t.me/BotFather)
- `HF_TOKEN` (опционально) — токен с https://huggingface.co/settings/tokens (тип **Read**). Без него тоже работает, но с токеном выше лимиты.

Сохрани файл.

### 5. Запусти бота

```bash
python bot.py
```

Увидишь `Bot starting...` — значит работает. Открой своего бота в Telegram, отправь `/start`, потом альбом из 2 фото.

## Как пользоваться

1. `/start` в чате с ботом
2. Прикрепи **2 фото одним альбомом** (скрепка → выбери обе фотки):
   - 1-я: твоё фото в полный рост (на однотонном фоне работает лучше)
   - 2-я: фото вещи
3. Подожди 1–3 минуты → получи результат

## Если HF Space не отвечает

Бесплатные Space-ы периодически:
- Засыпают (cold start ~30 сек после простоя)
- Перегружены (длинная очередь)
- Падают (GPU OOM, OOM памяти)

Если бот выдаёт ошибку — попробуй через минуту, или замени `HF_SPACE` в `.env` на альтернативный:
- `levihsu/OOTDiffusion`
- `Kwai-Kolors/Kolors-Virtual-Try-On`

## Что дальше (после MVP)

- 💳 Перейти на платный FASHN AI (~$0.04 за примерку) — стабильно, быстро
- 🗄 SQLite — гардероб юзера
- 👗 Сборка луков
- 🚀 Деплой на VPS с pm2
- 💰 Монетизация (Telegram Stars / ЮKassa)
