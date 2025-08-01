
from flask import Flask
from threading import Thread
import asyncio
from aiogram import Bot, Dispatcher, F
from aiogram.types import Message
from aiogram.filters import CommandStart, Command
from aiogram.client.default import DefaultBotProperties
from config import BOT_TOKEN
from gemini_api import ask_gemini
from limit_tracker import get_history, append_to_history, reset_history
import re
#сервер
app = Flask('')

@app.route('/')
def home():
    return "I'm alive!"

def run():
    app.run(host='0.0.0.0', port=8080)

def keep_alive():
    t = Thread(target=run)
    t.daemon = True
    t.start()




def escape_markdown(text: str) -> str:
    escape_chars = r'_*\[\]()~`>#+\-=|{}.!'
    return re.sub(f'([{re.escape(escape_chars)}])', r'\\\1', text)


bot = Bot(BOT_TOKEN, default=DefaultBotProperties(parse_mode="MarkdownV2"))
dp = Dispatcher(bot=bot)


@dp.message(CommandStart())
async def start_cmd(message: Message):
    await message.answer("Привет! Я бот с поддержкой Gemini 1.5 Flash.\nИспользуй /ask или упомяни меня.")

@dp.message(Command("help"))
async def help_cmd(message: Message):
    await message.answer(
        "инструкция:\n"
        "/ask [вопрос] — отправить запрос\n"
        "упомяни бота в чате — он ответит\n"
        "/help — помощь"
    )

@dp.message(Command("ask"))
@dp.message(Command("ask"))
async def ask_cmd(message: Message):
    text = message.text.removeprefix("/ask").strip()
    if not text:
        await message.answer("Напиши вопрос после /ask")
        return

    chat_id = message.chat.id
    history = get_history(chat_id)
    history.append({"role": "user", "text": text})

    loading_msg = await message.answer(escape_markdown("Обрабатываю запрос...(минутку)"))


    response = ask_gemini(history)

    # Удалить сообщение "Обрабатываю..."
    try:
        await loading_msg.delete()
    except:
        pass  # если нельзя удалить (например, недостаточно прав) — игнорируем

    if not response:
        await message.answer("Ошибка при обработке запроса.")
        return

    append_to_history(chat_id, text, response)
    await message.answer(escape_markdown(response))



@dp.message(F.text)
async def mention_handler(message: Message):
    if message.chat.type in ("group", "supergroup") and f"@{(await bot.me()).username}" in message.text:
        text = message.text.split(" ", 1)[1] if " " in message.text else ""
        if not text:
            await message.reply("Что ты хочешь спросить?")
            return
        chat_id = message.chat.id
        history = get_history(chat_id)
        history.append({"role": "user", "text": text})
        await message.reply("Секунду...")

        response = ask_gemini(history)
        if not response:
            await message.reply("Ошибка при запросе.")
            return

        append_to_history(chat_id, text, response)
        await message.reply(escape_markdown(response))


if __name__ == '__main__':
    keep_alive()
    import asyncio
    asyncio.run(dp.start_polling(bot))
