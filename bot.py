import asyncio
import logging
import os
import tempfile
from pathlib import Path

from aiogram import Bot, Dispatcher, F
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ChatAction, ParseMode
from aiogram.filters import CommandStart
from aiogram.types import FSInputFile, Message
from dotenv import load_dotenv
from gradio_client import Client, handle_file

load_dotenv()

BOT_TOKEN = os.environ["BOT_TOKEN"]
HF_SPACE = os.getenv("HF_SPACE", "yisol/IDM-VTON")
# gradio_client picks the token up from the HF_TOKEN env var automatically;
# we don't pass it as a kwarg because the parameter name varies between versions.

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
    "2️⃣ Фото вещи (одежды), которую хочешь примерить\n\n"
    "💡 В Telegram: жми скрепку 📎 → выбери обе фотки → отправь.\n"
    "💬 Можешь добавить <b>подпись</b> к альбому (например: «красный топ», "
    "«джинсы», «платье в цветочек») — это улучшит результат.\n\n"
    "⏱ Примерка занимает 1–3 минуты (бесплатная нейросеть, иногда очередь)."
)


class TryOnError(Exception):
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
    # Wait for the rest of the album messages to arrive.
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

    garment_des = next((p.caption.strip() for p in photos if p.caption), "clothing")[:100]

    status = await model_msg.answer("⏳ Скачиваю фото...")
    await bot.send_chat_action(model_msg.chat.id, ChatAction.UPLOAD_PHOTO)

    with tempfile.TemporaryDirectory() as tmp:
        tmp_dir = Path(tmp)
        try:
            model_path = await _download_photo(model_msg.photo[-1].file_id, tmp_dir / "model.jpg")
            garment_path = await _download_photo(garment_msg.photo[-1].file_id, tmp_dir / "garment.jpg")

            await status.edit_text("⏳ Примеряю на бесплатной нейросети (1–3 минуты)...")
            result_path = await asyncio.to_thread(_try_on, model_path, garment_path, garment_des)

            await model_msg.answer_photo(
                FSInputFile(result_path),
                caption="Готово! 💃 Хочешь ещё — присылай новый альбом.",
            )
            await status.delete()
        except TryOnError as e:
            log.warning("TryOn error: %s", e)
            await status.edit_text(
                f"❌ Не получилось: {e}\n\n"
                "Совет: попробуй повторить или другие фото. "
                "Бесплатный сервер бывает перегружен — иногда помогает подождать пару минут."
            )
        except Exception as e:
            log.exception("Unexpected error in _process_album")
            await status.edit_text(f"❌ Сбой: <code>{e}</code>")


async def _download_photo(file_id: str, dest: Path) -> Path:
    file = await bot.get_file(file_id)
    await bot.download_file(file.file_path, destination=dest)
    return dest


def _try_on(model_path: Path, garment_path: Path, garment_des: str) -> str:
    try:
        client = Client(HF_SPACE, verbose=False)
    except Exception as e:
        raise TryOnError(f"Не удалось подключиться к Hugging Face Space ({HF_SPACE}): {e}")

    try:
        result = client.predict(
            dict={
                "background": handle_file(str(model_path)),
                "layers": [],
                "composite": None,
            },
            garm_img=handle_file(str(garment_path)),
            garment_des=garment_des,
            is_checked=True,
            is_checked_crop=True,
            denoise_steps=40,
            seed=42,
            api_name="/tryon",
        )
    except Exception as e:
        raise TryOnError(f"Нейросеть вернула ошибку: {str(e)[:200]}")

    if isinstance(result, (list, tuple)) and result:
        first = result[0]
        if isinstance(first, str):
            return first
        if isinstance(first, dict) and "path" in first:
            return first["path"]
    if isinstance(result, str):
        return result
    raise TryOnError(f"Неожиданный формат ответа: {type(result).__name__}")


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
    log.info("Bot starting... space=%s", HF_SPACE)
    await dp.start_polling(bot)


if __name__ == "__main__":
    asyncio.run(main())
