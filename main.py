import asyncio
import os
from aiogram import Bot, Dispatcher, executor, types
from finhub import get_news, get_market_news
from gemini_analyze import analyze_pdf
from graph_yf import graph, news as yf_news, get_recommendations_summary
from investgemini import invest_gemini
from aiogram.types import (
    CallbackQuery,
    InlineKeyboardButton,
    InlineKeyboardMarkup,
    KeyboardButton,
    ParseMode,
    ReplyKeyboardMarkup,
)
from dotenv import load_dotenv

load_dotenv()

keyboard = ReplyKeyboardMarkup(
    keyboard=[
        [
            KeyboardButton(text='Анализ банковской выписки💳'),
            KeyboardButton(text='Лучшие компании для инвестирования! 🌐')
        ],
        [
        KeyboardButton(text="График цен акции"),
        ],
        [
            KeyboardButton(text="Функции"),
        ]
    ],
    resize_keyboard=True,
)

keyboard_functions = ReplyKeyboardMarkup(
    keyboard=[
        [
            KeyboardButton(text="Получить новости рынка"),
            KeyboardButton(text="Получить новости компании"),
        ],
        [
            KeyboardButton(text="Рекомендации"),
            KeyboardButton(text="Новости Yahoo Finance"),
        ],
        [
            KeyboardButton(text="Назад"),
        ],
    ],
    resize_keyboard=True,
)




USER_STATE = {}
TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN")
bot = Bot(token=TELEGRAM_TOKEN)
dp = Dispatcher(bot)


@dp.message_handler(commands=["start"])
async def handle_start(message: types.Message):
    USER_STATE[message.from_user.id] = ""
    welcome_msg = """🚀 Добро пожаловать в мир инвестиций с Tiyin! 📈

Ты хочешь увеличить свои доходы и стать успешным инвестором? Не знаешь, с какой акции начать? Мы здесь, чтобы помочь тебе в этом увлекательном путешествии!

✨ Что делает Tiyin для тебя:

📊 Анализ Рынка: Наш искусственный интеллект ежедневно сканирует рынок, выявляя перспективные акции для инвестирования.

🔍 Точные Рекомендации: Получай точные рекомендации от нашего бота, основанные на глубоком анализе данных и трендов.

💡 Образование и Советы: Узнавай новые стратегии, получай образовательный контент и советы от опытных инвесторов.

🔄 Постоянное Обновление: Мы постоянно обновляем информацию, чтобы ты всегда был в курсе последних событий на финансовых рынках.

🔒 Безопасность и Прозрачность: Твои данные в безопасности, а наши рекомендации прозрачны и обоснованы.

🚀 Стань успешным инвестором с Tiyin прямо сейчас!

Присоединяйся к нам и давай зарабатывать вместе! 💰

📈 Не упусти свой шанс на финансовый успех с Tiyin! 🚀"""
    await bot.send_message(message.chat.id, welcome_msg, reply_markup=keyboard)

@dp.message_handler(
    lambda message: message.text == "Лучшие компании для инвестирования! 🌐"
)
async def handle_test_gpt(message: types.Message):
    image_path = "generated_image.png"
    with open(image_path, "rb") as image_file:
        await bot.send_photo(message.chat.id, photo=image_file)
    loading_message = await message.reply("Загрузка...")
    response = invest_gemini()
    await asyncio.sleep(2)

    await bot.edit_message_text(
        response, chat_id=loading_message.chat.id, message_id=loading_message.message_id
    )

@dp.message_handler(lambda message: message.text == "Функции")
async def handle_functions(message: types.Message):
    await message.reply("Выберите функцию:", reply_markup=keyboard_functions)


@dp.message_handler(lambda message: message.text == "Назад")
async def handle_functions(message: types.Message):
    await message.reply(text="Вы вернулись в главное меню", reply_markup=keyboard)

@dp.message_handler(lambda message: message.text == "Рекомендации")
async def handle_recommendations(message: types.Message):
    USER_STATE[message.from_user.id] = message.text
    await message.answer("Введите тикер компании:")


@dp.message_handler(lambda message: message.text == "Новости Yahoo Finance")
async def handler_company_news(message: types.Message):
    USER_STATE[message.from_user.id] = message.text
    await message.answer("Введите тикер компании:")

@dp.message_handler(lambda message: message.text == "График цен акции")
async def handler_graph(message: types.Message):
    USER_STATE[message.from_user.id] = message.text
    await message.answer("Введите тикер компании:")

@dp.message_handler(lambda message: message.text == "Получить новости рынка")
async def handle_market_news(message: types.Message):
    response = get_market_news()
    await message.reply(
        response, parse_mode=types.ParseMode.MARKDOWN, reply_markup=keyboard
    )

@dp.message_handler(lambda message: message.text == "Получить новости компании")
async def handler_company_news(message: types.Message):
    USER_STATE[message.from_user.id] = message.text
    await message.answer("Введите тикер компании:")
    
@dp.message_handler(lambda message: message.text == "Анализ банковской выписки💳")
async def handler_company_news(message: types.Message):
    USER_STATE[message.from_user.id] = message.text
    await message.answer("Отправьте банковские выписки (в формате PDF):")

@dp.message_handler(content_types=types.ContentTypes.DOCUMENT)
async def process_pdf_document(message: types.Message):
    if USER_STATE[message.from_user.id] == "Анализ банковской выписки💳":
        if message.document.mime_type == 'application/pdf':
            file_object = await message.document.download(destination_file=f'{message.document.file_id}.pdf')
            file_path = str(file_object.name)
            file_object.close()
            loading_message = await message.reply_video(video="BAACAgIAAxkBAAIII2YxUPJsbIZWuMUd_gRJiCNlF6qpAALVRwACrFGIScoTcPu3ueTpNAQ")
            try:
                response = analyze_pdf(file_path)
            finally:
                await asyncio.sleep(2) 
                os.remove(file_path)

            USER_STATE[message.from_user.id] = ''
            await bot.delete_message(chat_id=message.chat.id, message_id=loading_message.message_id)
            
            await message.reply(response)
        else:
            await message.answer("Пожалуйста, отправьте файл в формате PDF.")
    
@dp.message_handler(content_types=types.ContentTypes.TEXT)
async def process_ticker(message: types.Message):
    try:
        if USER_STATE[message.from_user.id] == "График цен акции":
            ticker = message.text.upper()
            image_path = graph(ticker)
            with open(image_path, "rb") as photo:
                await message.reply_photo(photo, caption=f"{ticker} Stock Price Over Time")
            os.remove(image_path)
            USER_STATE[message.from_user.id] = ""
        
        elif USER_STATE[message.from_user.id] == "Новости Yahoo Finance":
            ticker = message.text.upper()
            response = yf_news(ticker)
            
            await message.answer(
                response, parse_mode=types.ParseMode.MARKDOWN, reply_markup=keyboard
            )
            USER_STATE[message.from_user.id] = ""
            
        elif USER_STATE[message.from_user.id] == "Рекомендации":
            ticker = message.text.upper()
            response = get_recommendations_summary(ticker)
            
            await message.answer(
                response, parse_mode=types.ParseMode.MARKDOWN, reply_markup=keyboard
            )
            USER_STATE[message.from_user.id] = ""
        
        elif USER_STATE[message.from_user.id] == "Получить новости компании":
            ticker = message.text.upper()
            response = get_news(ticker)

            await message.answer(
                response, reply_markup=keyboard
            )
            USER_STATE[message.from_user.id] = ""
        else:
            pass
    except:
        pass

                
if __name__ == "__main__":
    executor.start_polling(dp, skip_updates=True)
