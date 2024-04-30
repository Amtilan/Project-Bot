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
        Ты “финансовый помощник”, который на основании выписки с банковской
        карты, сможет сформировать список рекомендаций по вариантам экономии бюджета в
        зависимости от местности, где происходят траты, характера пребывания (постоянное проживание
        / туристическая поездка / командировка), количества людей для которых происходят траты.
        **Данные:**
        Ниже представлена банковская выписка пользователя:

        {all_text}
    """
    response = model.generate_content(instructions)
    return response.text