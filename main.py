import asyncio
import os
from aiogram import Bot, Dispatcher, executor, types
from finhub import get_news, get_market_news
from gemini_analyze import analyze_pdf
import datetime
from graph_yf import graph, news as yf_news, get_recommendations_summary
from investgemini import invest_gemini, get_curent, check_for_value
from mongo_fetch import update_and_save_data, is_allowed_user
from ask_gemini import askbot, spehere
import logging
from aiogram.types import (
    CallbackQuery,
    InlineKeyboardButton,
    InlineKeyboardMarkup,
    KeyboardButton,
    ReplyKeyboardMarkup,
)
from dotenv import load_dotenv

load_dotenv()

keyboard = ReplyKeyboardMarkup(
    keyboard=[
        [
            # KeyboardButton(text='Анализ банковской выписки💳'),
            KeyboardButton(text='Лучшие компании для инвестирования! 🌐')
        ],
        [
            KeyboardButton(text="Сектора"),
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
keyboard_storage = {}
PICK_STATE = {}
USER_STATE = {}
TELEGRAM_TOKEN = os.getenv("TELEGRAM_API_TOKEN1")
bot = Bot(token=TELEGRAM_TOKEN)
dp = Dispatcher(bot)


@dp.message_handler(commands=["start"])
async def handle_start(message: types.Message):
    if not is_allowed_user(message.from_user.id):
        await message.reply("У вас нет прав для использования этой команды.")
        return
    
    USER_STATE[message.from_user.id] = ""
    welcome_msg = """🚀 Добро пожаловать в мир инвестиций с Narasense AI! 📈

Ты хочешь увеличить свои доходы и стать успешным инвестором? Не знаешь, с какой акции начать? Мы здесь, чтобы помочь тебе в этом увлекательном путешествии!

✨ Что делает Narasense AI для тебя:

📊 Анализ Рынка: Наш искусственный интеллект ежедневно сканирует рынок, выявляя перспективные акции для инвестирования.

🔍 Точные Рекомендации: Получай точные рекомендации от нашего бота, основанные на глубоком анализе данных и трендов.

💡 Образование и Советы: Узнавай новые стратегии, получай образовательный контент и советы от опытных инвесторов.

🔄 Постоянное Обновление: Мы постоянно обновляем информацию, чтобы ты всегда был в курсе последних событий на финансовых рынках.

🔒 Безопасность и Прозрачность: Твои данные в безопасности, а наши рекомендации прозрачны и обоснованы.

🚀 Стань успешным инвестором с Narasense AI прямо сейчас!

Присоединяйся к нам и давай зарабатывать вместе! 💰

📈 Не упусти свой шанс на финансовый успех с Narasense AI! 🚀"""
    await bot.send_message(message.chat.id, welcome_msg , reply_markup=keyboard)

@dp.message_handler(
    lambda message: message.text == "Сектора"
)
async def handle_test_gpt(message: types.Message):
    if not is_allowed_user(message.from_user.id):
        await message.reply("У вас нет прав для использования этой команды.")
        return
    loading_message = await message.reply("Загрузка...")
    response = spehere()
    await asyncio.sleep(2)

    await bot.edit_message_text(
        response, chat_id=loading_message.chat.id, message_id=loading_message.message_id
    )


async def daily_task():
    await update_and_save_data()

async def run_daily_task_at_specific_time(target_time):
    while True:
        now = datetime.datetime.now()
        future = datetime.datetime.combine(now.date(), target_time)
        if now.time() > target_time:
            future += datetime.timedelta(days=1)
        wait_seconds = (future - now).total_seconds()
        logging.info(f"Next run in {wait_seconds} seconds")
        await asyncio.sleep(wait_seconds)
        await daily_task()

async def on_startup(_):
    target_time = datetime.time(10, 0) 
    asyncio.create_task(run_daily_task_at_specific_time(target_time))


@dp.message_handler(commands=['ask'])
async def askgpt(message: types.Message):
    if not is_allowed_user(message.from_user.id):
        await message.reply("У вас нет прав для использования этой команды.")
        return
    loading_message = await message.reply("Загрузка...")
    response = askbot(message.text)
    await asyncio.sleep(2)

    await bot.edit_message_text(
    text=response,
    chat_id=loading_message.chat.id,
    message_id=loading_message.message_id,
)

@dp.callback_query_handler(lambda c: c.data and c.data.startswith('invest_'))
async def handle_investment(callback_query: CallbackQuery):
    company_name = callback_query.data[len('invest_'):]
    if company_name != 'explanation':

        keyboard1 = InlineKeyboardMarkup()
        companies = get_curent(name=company_name)
        
                
        info = companies['data'][0]['data']
        
        response_text = f"""
<b>Вы выбрали инвестировать в компанию {company_name}</b>
<i>Вот дополнительная информация:</i>

<b>ISIN:</b> <code>{companies['isin']}</code>
"""

        # Условные добавления строк
        if info.get('last_balance_year'):
            response_text += f"<b>Последний год баланса:</b> {info['last_balance_year']}\n"

        if info.get('market_capitalization'):
            response_text += f"<b>Рыночная капитализация:</b> ${info['market_capitalization']:,.2f}\n"

        ebit_margin = info.get('ebit_margin')
        if ebit_margin and ebit_margin.get('value') is not None:
            response_text += f"<b>Маржа EBIT:</b> {ebit_margin['value']:.2f}% {check_for_value(ebit_margin['point'])}\n"

        equity_ratio = info.get('equity_ratio_in_percent')
        if equity_ratio and equity_ratio.get('value') is not None:
            response_text += f"<b>Коэффициент собственного капитала:</b> {equity_ratio['value']:.2f}% {check_for_value(equity_ratio['point'])}\n"

        return_equity = info.get('return_equity')
        if return_equity and return_equity.get('value') is not None:
            response_text += f"<b>Доходность собственного капитала:</b> {return_equity['value']:.2f}% {check_for_value(return_equity['point'])}\n"

        pe_ratio_5y = info.get('price_earnings_ratio_5y')
        if pe_ratio_5y and pe_ratio_5y.get('value') is not None:
            response_text += f"<b>P/E Ratio (5 лет):</b> {pe_ratio_5y['value']:.2f} {check_for_value(pe_ratio_5y['point'])}\n"

        pe_ratio_ay = info.get('price_earnings_ratio_ay')
        if pe_ratio_ay and pe_ratio_ay.get('value') is not None:
            response_text += f"<b>P/E Ratio (текущий год):</b> {pe_ratio_ay['value']:.2f} {check_for_value(pe_ratio_ay['point'])}\n"

        profit_growth = info.get('profit_growth')
        if profit_growth and profit_growth.get('value') is not None:
            response_text += f"<b>Рост прибыли:</b> {profit_growth['value']} {check_for_value(profit_growth['point'])}\n"

        share_price_m6 = info.get('share_price_m6_comparison')
        if share_price_m6 and share_price_m6.get('value') is not None:
            response_text += f"<b>Сравнение цены акции (6 мес.):</b> {share_price_m6['value']} {check_for_value(share_price_m6['point'])}\n"

        share_price_y1 = info.get('share_price_y1_comparison')
        if share_price_y1 and share_price_y1.get('value') is not None:
            response_text += f"<b>Сравнение цены акции (1 год):</b> {share_price_y1['value']} {check_for_value(share_price_y1['point'])}\n"

        share_price_momentum = info.get('share_price_momentum')
        if share_price_momentum and share_price_momentum.get('value') is not None:
            response_text += f"<b>Моментум цены акции:</b> {share_price_momentum['value']} {check_for_value(share_price_momentum['point'])}\n"

        total_points = info.get('total_points')
        if total_points and total_points.get('point') is not None and total_points.get('value') is not None:
            response_text += f"<b>Общее количество баллов:</b> {total_points['point']} из {total_points['value']}\n"

    else:
        
        response_text = """
<b>Объяснение критериев оценки:</b>

<b>ISIN:</b> Международный идентификационный номер ценной бумаги для уникальной идентификации.

<b>Последний год баланса:</b> Год, за который был составлен последний финансовый баланс компании.

<b>Рыночная капитализация:</b> Общая стоимость компании на фондовом рынке.

<b>Маржа EBIT:</b> Процент прибыли до вычета процентов и налогов от общей выручки.

<b>Коэффициент собственного капитала:</b> Процент собственного капитала компании относительно всех ее активов.

<b>Доходность собственного капитала:</b> Прибыль, полученная на каждый доллар собственного капитала.

<b>P/E Ratio (5 лет):</b> Среднее соотношение цены и прибыли за последние пять лет.

<b>P/E Ratio (текущий год):</b> Соотношение цены и прибыли за текущий год.

<b>Рост прибыли:</b> Изменение прибыли компании за определенный период времени.

<b>Сравнение цены акции (6 мес.):</b> Изменение цены акции за последние шесть месяцев.

<b>Сравнение цены акции (1 год):</b> Изменение цены акции за последний год.

<b>Моментум цены акции:</b> Тенденция изменения цены акции с течением времени.

<b>Общее количество баллов:</b> Итоговый показатель инвестиционной привлекательности компании.
    """
    keyboard1 = keyboard_storage.get(callback_query.message.message_id, InlineKeyboardMarkup())
    
    await bot.edit_message_text(
        text=response_text,
        chat_id=callback_query.message.chat.id,
        message_id=callback_query.message.message_id,
        reply_markup=keyboard1,
        parse_mode='HTML'
    )
    await callback_query.answer()

@dp.message_handler(
    lambda message: message.text == "Лучшие компании для инвестирования! 🌐"
)
async def handle_test_gpt(message: types.Message):
    if not is_allowed_user(message.from_user.id):
        await message.reply("У вас нет прав для использования этой команды.")
        return
    image_path = "generated_image.png"
    with open(image_path, "rb") as image_file:
        await bot.send_photo(message.chat.id, photo=image_file)
    
    loading_message = await message.reply("Загрузка...")
    
    response, companies = invest_gemini()
    await asyncio.sleep(2)
    keyboard1 = InlineKeyboardMarkup()
    if message.chat.id not in keyboard_storage:
        keyboard1 = InlineKeyboardMarkup()
        for company in companies:
            button = InlineKeyboardButton(text=company["name"], callback_data=f'invest_{company["name"]}')
            keyboard1.add(button)
        button = InlineKeyboardButton(text="Обьяснение оценок", callback_data=f'invest_explanation')
        keyboard1.add(button)
    
        keyboard_storage[loading_message.message_id] = keyboard1
    else:
        keyboard1 = keyboard_storage[loading_message.message_id]

    await bot.edit_message_text(
        text=response,
        chat_id=loading_message.chat.id,
        message_id=loading_message.message_id,
        reply_markup=keyboard1
    )

@dp.message_handler(lambda message: message.text == "Функции")
async def handle_functions(message: types.Message):
    if not is_allowed_user(message.from_user.id):
        await message.reply("У вас нет прав для использования этой команды.")
        return
    await message.reply("Выберите функцию:", reply_markup=keyboard_functions)


@dp.message_handler(lambda message: message.text == "Назад")
async def handle_functions(message: types.Message):
    if not is_allowed_user(message.from_user.id):
        await message.reply("У вас нет прав для использования этой команды.")
        return
    await message.reply(text="Вы вернулись в главное меню", reply_markup=keyboard)

@dp.message_handler(lambda message: message.text == "Рекомендации")
async def handle_recommendations(message: types.Message):
    if not is_allowed_user(message.from_user.id):
        await message.reply("У вас нет прав для использования этой команды.")
        return
    USER_STATE[message.from_user.id] = message.text
    await message.answer("Введите тикер компании:")


@dp.message_handler(lambda message: message.text == "Новости Yahoo Finance")
async def handler_company_news(message: types.Message):
    if not is_allowed_user(message.from_user.id):
        await message.reply("У вас нет прав для использования этой команды.")
        return
    USER_STATE[message.from_user.id] = message.text
    await message.answer("Введите тикер компании:")

@dp.message_handler(lambda message: message.text == "График цен акции")
async def handler_graph(message: types.Message):
    if not is_allowed_user(message.from_user.id):
        await message.reply("У вас нет прав для использования этой команды.")
        return
    USER_STATE[message.from_user.id] = message.text
    await message.answer("Введите тикер компании:")

@dp.message_handler(lambda message: message.text == "Получить новости рынка")
async def handle_market_news(message: types.Message):
    if not is_allowed_user(message.from_user.id):
        await message.reply("У вас нет прав для использования этой команды.")
        return
    response = get_market_news()
    await message.reply(
        response, parse_mode=types.ParseMode.MARKDOWN, reply_markup=keyboard
    )

@dp.message_handler(lambda message: message.text == "Получить новости компании")
async def handler_company_news(message: types.Message):
    if not is_allowed_user(message.from_user.id):
        await message.reply("У вас нет прав для использования этой команды.")
        return
    USER_STATE[message.from_user.id] = message.text
    await message.answer("Введите тикер компании:")
    
@dp.message_handler(lambda message: message.text == "Анализ банковской выписки💳")
async def handler_company_news(message: types.Message):
    if not is_allowed_user(message.from_user.id):
        await message.reply("У вас нет прав для использования этой команды.")
        return
    USER_STATE[message.from_user.id] = message.text
    await message.answer("Отправьте банковские выписки (в формате PDF):")

@dp.message_handler(content_types=types.ContentTypes.DOCUMENT)
async def process_pdf_document(message: types.Message):
    if not is_allowed_user(message.from_user.id):
        await message.reply("У вас нет прав для использования этой команды.")
        return
    if USER_STATE[message.from_user.id] == "Анализ банковской выписки💳":
        if message.document.mime_type == 'application/pdf':
            file_object = await message.document.download(destination_file=f'{message.document.file_id}.pdf')
            file_path = str(file_object.name)
            file_object.close()
            loading_message = await message.reply_video(video="BAACAgIAAxkBAAMlZjJ6-k5XtwkPm9PY1OxWYDxs2CAAAtVHAAKsUYhJ7PMoM71siCY0BA", caption="Енот анализирует ваши данные!")
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