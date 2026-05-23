import asyncio
import logging
import os

import httpx
from aiogram import Bot, Dispatcher, F
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ChatAction, ParseMode
from aiogram.filters import CommandStart
from aiogram.types import Message
from dotenv import load_dotenv

load_dotenv()

BOT_TOKEN = os.environ["BOT_TOKEN"]
FASHN_API_KEY = os.environ["FASHN_API_KEY"]
FASHN_BASE = "https://api.fashn.ai/v1"
FASHN_MODEL = os.getenv("FASHN_MODEL", "tryon-v1.6")

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(levelname)s | %(name)s | %(message)s",
)
log = logging.getLogger("fitting-bot")

bot = Bot(BOT_TOKEN, default=DefaultBotProperties(parse_mode=ParseMode.HTML))
dp = Dispatcher()

album_buffer: dict[str, list[Message]] = {}

WELCOME = (
    "Привет! 👗 Я — бот-примерочная.\n\n"
    "Пришли мне <b>ОДНИМ альбомом 2 фото</b>:\n"
    "1️⃣ Своё фото в полный рост\n"
    "2️⃣ Фото вещи, которую хочешь примерить\n\n"
    "💡 В Telegram: жми скрепку 📎 → выбери обе фотки → отправь.\n\n"
    "⏱ Обработка занимает 20-40 секунд."
)


class FashnError(Exception):
    pass


@dp.message(CommandStart())
async def cmd_start(message: Message) -> None:
    await message.answer(WELCOME)


@dp.message(F.media_group_id, F.photo)
async def handle_album_photo(message: Message) -> None:
    gid = message.media_group_id
    is_first = gid not in album_buffer
    album_buffer.setdefault(gid, []).append(message)
    if is_first:
        asyncio.create_task(_process_album(gid))


async def _process_album(gid: str) -> None:
    # Wait for the rest of the album to arrive (Telegram sends each photo as a separate update).
    await asyncio.sleep(1.5)
    photos = album_buffer.pop(gid, [])
    if not photos:
        return

    if len(photos) < 2:
        await photos[0].answer(
            "Нужно <b>2 фото</b> в одном альбоме: фото себя + фото вещи."
        )
        return

    photos.sort(key=lambda m: m.message_id)
    model_msg, garment_msg = photos[0], photos[1]

    status = await model_msg.answer("⏳ Готовлю примерку, ~30 секунд...")
    await bot.send_chat_action(model_msg.chat.id, ChatAction.UPLOAD_PHOTO)

    try:
        model_url = await _telegram_file_url(model_msg.photo[-1].file_id)
        garment_url = await _telegram_file_url(garment_msg.photo[-1].file_id)
        result_url = await _try_on(model_url, garment_url)
        await model_msg.answer_photo(
            result_url,
            caption="Готово! 💃 Хочешь ещё — присылай новый альбом.",
        )
        await status.delete()
    except FashnError as e:
        log.warning("FASHN error: %s", e)
        await status.edit_text(
            f"❌ Не получилось: {e}\n\n"
            "Совет: фото человека в полный рост на однотонном фоне работает лучше всего."
        )
    except Exception as e:
        log.exception("Unexpected error in _process_album")
        await status.edit_text(f"❌ Сбой: <code>{e}</code>")


async def _telegram_file_url(file_id: str) -> str:
    file = await bot.get_file(file_id)
    return f"https://api.telegram.org/file/bot{BOT_TOKEN}/{file.file_path}"


async def _try_on(model_url: str, garment_url: str) -> str:
    async with httpx.AsyncClient(timeout=120.0) as client:
        run = await client.post(
            f"{FASHN_BASE}/run",
            headers={"Authorization": f"Bearer {FASHN_API_KEY}"},
            json={
                "model_name": FASHN_MODEL,
                "inputs": {
                    "model_image": model_url,
                    "garment_image": garment_url,
                    "category": "auto",
                },
            },
        )
        if run.status_code >= 400:
            raise FashnError(f"FASHN /run {run.status_code}: {run.text[:200]}")
        data = run.json()
        if data.get("error"):
            raise FashnError(str(data["error"]))
        pred_id = data["id"]
        log.info("FASHN prediction started: %s", pred_id)

        for _ in range(60):
            await asyncio.sleep(2)
            sr = await client.get(
                f"{FASHN_BASE}/status/{pred_id}",
                headers={"Authorization": f"Bearer {FASHN_API_KEY}"},
            )
            if sr.status_code >= 400:
                raise FashnError(f"FASHN /status {sr.status_code}: {sr.text[:200]}")
            sdata = sr.json()
            status = sdata.get("status")
            if status == "completed":
                output = sdata.get("output") or []
                if not output:
                    raise FashnError("Нейросеть вернула пустой результат")
                return output[0]
            if status == "failed":
                raise FashnError(str(sdata.get("error") or "failed"))
        raise FashnError("Тайм-аут ожидания результата")


@dp.message(F.photo)
async def handle_single_photo(message: Message) -> None:
    await message.answer(
        "Пришли <b>2 фото в одном альбоме</b>:\n"
        "📎 → выбери фото себя И фото вещи → отправь одним сообщением."
    )


@dp.message()
async def handle_other(message: Message) -> None:
    await message.answer(WELCOME)


async def main() -> None:
    log.info("Bot starting... model=%s", FASHN_MODEL)
    await dp.start_polling(bot)


if __name__ == "__main__":
    asyncio.run(main())
