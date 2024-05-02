import os
from dotenv import load_dotenv
from google import generativeai as genai
from PyPDF2 import PdfReader

def get_pdf_text(pdf_path):
    if not os.path.exists(pdf_path):
        raise FileNotFoundError(f"No file found at the provided path: {pdf_path}")

    text = ""
    with open(pdf_path, 'rb') as file:
        pdf_reader = PdfReader(file)
        for page_num, page in enumerate(pdf_reader.pages):
            page_text = page.extract_text()
            if page_text:
                text += f"--- PAGE {page_num+1} ---\n"
                text += page_text + "\n"
    return text

def analyze_pdf(file_path):
    load_dotenv()
    genai.configure(api_key=os.getenv('GEMINI_API_KEY'))

    generation_config = {
        "temperature": 0.3,
        "top_p": 1,
        "top_k": 1,
        "max_output_tokens": 90000,
    }

    safety_settings = [
        {"category": "HARM_CATEGORY_HARASSMENT", "threshold": "BLOCK_NONE"},
        {"category": "HARM_CATEGORY_HATE_SPEECH", "threshold": "BLOCK_NONE"},
        {"category": "HARM_CATEGORY_SEXUALLY_EXPLICIT", "threshold": "BLOCK_NONE"},
        {"category": "HARM_CATEGORY_DANGEROUS_CONTENT", "threshold": "BLOCK_NONE"},
    ]

    model = genai.GenerativeModel(
        model_name="gemini-1.5-pro-latest",
        generation_config=generation_config,
        safety_settings=safety_settings
    )

    try:
        all_text = get_pdf_text(file_path)
    except FileNotFoundError as e:
        return str(e)
    except Exception as e:
        return f"An error occurred: {e}"

    instructions = f"""
        ## Анализ банковской выписки и рекомендации по экономии

        Цель: 
        Проанализировать предоставленную банковскую выписку и сформировать 
        рекомендации по экономии бюджета, учитывая:
        * Местность (страна, город) где происходят траты.
        * Характер пребывания (постоянное проживание / туристическая поездка / командировка).
        * Количество человек, для которых происходят траты.
        * Сравнение с тратами других пользователей в той же местности.

        Вывод:
        1. Таблица с прогнозом:  предположите, сколько денег у человека останется,
           если он будет следовать всем вашим рекомендациям.
        2. Рекомендации: предложи 3 конкретных способа экономии по категориям трат с фокусом на уменьшение задолжностей. Учитывай что кредиты должны быть выплачены в первую очередь. Идеальным планом расходов считать траты 65% на обязательные расходы, 25% на развлечения и 10% инвестирования.
        Хочется более короткие и понятные рекомендации (сейчас у многих лонгрид), лонгриды реальный пользователь читать не будет. Ему нужно дать коротко: ты слишком часто посещаешь рестораны. Ходи максимум 1 раз в неделю вместо 3. Так ты сэкономишь N тенге в месяц. 
        На продукты у вас выходит столько то денег: возможно вы курите, бросайте, это вам сэкономит N денег и M лет здоровья :). В среднем в (стране) можно уложиться в N в месяц. (И рекомендовать засчет чего можно оптимизировать) 
        В целом хочется тут больше с продуктом поиграть и с подачей, *чтобы ознакомившись с ним реально захотелось пользователю экономить. *
        Данные:
        Ниже представлена банковская выписка пользователя:

        {all_text}
    """
    response = model.generate_content(instructions)
    return response.text
