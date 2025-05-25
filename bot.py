import asyncio
import json
import random
from datetime import datetime
import os
from aiogram import Bot, Dispatcher, F
from aiogram.types import Message, KeyboardButton, ReplyKeyboardMarkup
from aiogram.filters import Command
from apscheduler.schedulers.asyncio import AsyncIOScheduler
import pytz
from dotenv import load_dotenv
load_dotenv()



CHAT_ID_NASTYA = int(os.getenv("NASTYA_CHAT_ID"))
bot = Bot(token=os.getenv("BOT_TOKEN"))
dp = Dispatcher()

morning_messages = [
    "Доброе утро, Настенька! 🌞 Пусть этот день принесёт тебе улыбки, лёгкость и капельку волшебства!",
    "Просыпайся, Настя! ☀️ Сегодня — идеальный день для маленьких радостей и больших свершений!",
    "Доброе утро, Настя! 💖 Пусть всё сложится именно так, как ты захочешь, а день будет добрым и светлым!",
    "Насть, доброе утро! 🌸 Пусть сегодня тебя ждёт что-то прекрасное и волшебное",
    "Доброе утро, Настя! 🌈 Пусть день будет таким же ярким, как твои глаза, и таким же тёплым, как твоё сердце!",
    "Проснись и улыбнись! 😊 Сегодняшний день создан для счастья — не упусти его!",
    "Настенька, доброе утро! 🌹 Пусть сегодня всё получается легко, а любая грусть растворяется в твоей улыбке!",
    "Утро началось, а значит, где-то рядом уже ждёт что-то хорошее! ✨ Держи хвост пистолетом, красавица!",
    "Доброе утро, Настя! 🐇 Пусть день будет наполнен приятными моментами, а все тревоги обойдут тебя стороной!",
    "Солнце светит специально для тебя! ☀️💛 Пусть этот день подарит тебе вдохновение и сотню поводов для радости!"
]

emotion_responses = {
    "Мне грустно 😢": "Не грусти, Настенька! Вот обнимашки тебе 🤗 и немного тепла 💖",
    "Мне одиноко 🏠": "Настя, не переживай! Ты не одна, я всегда с тобой! 🌸",
    "Мне весело 😊": "Здорово! Пусть улыбка не сходит с лица 😄 Вот тебе лучик радости ☀️",
    "Заебла эта учёба 📚": "Учёба — это сложно, но ты справишься! 💪 Вот немного мотивации 🌟"
}

EMOTIONS_FILE = "emotions.json"

keyboard = ReplyKeyboardMarkup(
    keyboard=[
        [
            KeyboardButton(text="Мне грустно 😢"),
            KeyboardButton(text="Мне одиноко 🏠"),
        ],
        [
            KeyboardButton(text="Мне весело 😊"),
            KeyboardButton(text="Заебла эта учёба 📚"),
        ],
        [
            KeyboardButton(text="Дневник эмоций 📔"),
        ],
    ],
    resize_keyboard=True
)

moscow_tz = pytz.timezone("Europe/Moscow")


def save_emotion(user_id: int, emotion: str):
    now = datetime.now(moscow_tz).strftime("%Y-%m-%d %H:%M:%S")
    entry = {"user_id": user_id, "emotion": emotion, "timestamp": now}

    try:
        with open(EMOTIONS_FILE, "r", encoding="utf-8") as f:
            data = json.load(f)
    except (FileNotFoundError, json.JSONDecodeError):
        data = []

    data.append(entry)

    with open(EMOTIONS_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)


async def send_morning_message():
    message = random.choice(morning_messages)
    await bot.send_message(CHAT_ID_NASTYA, message)


async def send_evening_message():
    await bot.send_message(CHAT_ID_NASTYA, "Привет, Настя! Какое у тебя сегодня настроение?🌸")


@dp.message(Command("start"))
async def cmd_start(message: Message):
    if message.from_user.id != CHAT_ID_NASTYA:
        await message.answer("Извините, этот бот только для Насти 😊")
        return
    await message.answer(
        "Привет, Настя! Я твой дневник эмоций 🌸\n"
        "Используй кнопки ниже, чтобы поделиться настроением или посмотреть дневник эмоций.",
        reply_markup=keyboard,
    )


@dp.message(F.text.in_(emotion_responses.keys()))
async def handle_emotion(message: Message):
    if message.from_user.id != CHAT_ID_NASTYA:
        await message.answer("Извините, этот бот только для Насти 😊")
        return

    emotion = message.text
    save_emotion(message.from_user.id, emotion)
    response = emotion_responses[emotion]
    await message.answer(response)


@dp.message(F.text == "Дневник эмоций 📔")
async def show_emotions_log(message: Message):
    if message.from_user.id != CHAT_ID_NASTYA:
        await message.answer("Извините, этот бот только для Насти 😊")
        return

    try:
        with open(EMOTIONS_FILE, "r", encoding="utf-8") as f:
            data = json.load(f)
    except (FileNotFoundError, json.JSONDecodeError):
        data = []

    if not data:
        await message.answer("Дневник эмоций пока пуст 😌")
        return

    log_messages = []
    for entry in data[-10:]:
        time = entry["timestamp"]
        emo = entry["emotion"]
        log_messages.append(f"{time}: {emo}")

    await message.answer("📔 Твой дневник эмоций (последние записи):\n\n" + "\n".join(log_messages))


async def scheduler_jobs():
    scheduler = AsyncIOScheduler(timezone=moscow_tz)
    scheduler.add_job(send_morning_message, "cron", hour=1, minute=40)
    scheduler.add_job(send_evening_message, "cron", hour=1, minute=41)
    scheduler.start()


async def main():
    await scheduler_jobs()
    await dp.start_polling(bot)


if __name__ == "__main__":
    asyncio.run(main())
