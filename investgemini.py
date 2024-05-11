from dotenv import load_dotenv
import os
import google.generativeai as genai
import random
import json

def get_json_text(json_path):
    if not os.path.exists(json_path):
        raise FileNotFoundError(f"No file found at the provided path: {json_path}")

    with open(json_path, 'r') as file:
        data = json.load(file)
    
    if not isinstance(data, list):
        raise ValueError("Expected a list of items in the JSON file")

    random_items = random.sample(data, min(len(data), 3))

    formatted_random_items = json.dumps(random_items, indent=4)
    
    return formatted_random_items

def invest_gemini():
    load_dotenv()

    genai.configure(api_key=os.getenv('GEMINI_API_KEY'))
    model = genai.GenerativeModel('gemini-1.5-pro-latest')

    json_file_path = 'results.json'
    
    user_question = """
    Как профессиональный экономист и финансист, вы обладаете уникальной способностью 
    точно предсказывать движение акций. Ваша задача - представить рекомендации по акциям 
    в заманчивой манере, вызвав у читателя интерес к рассмотрению этих инвестиций. 
    Сохраняйте профессиональный тон и предлагайте разумные инвестиционные рекомендации. 

    Указывайте только названия компаний и их тикерные метки, 
    оформляя каждую рекомендацию в приятном для чтения стиле, 
    который привлекает потенциальных инвесторов. 

    Пожалуйста, поделитесь 3 такими рекомендациями.
    """
    data = get_json_text(json_file_path)

    user_question += f"\n\nВыберите три акции из следующего списка: {data}"
    response = model.generate_content(user_question)

    if response.text:
        return response.text
    else:
        return ""
    
    

