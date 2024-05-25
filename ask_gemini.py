import os 
from dotenv import load_dotenv
from google import generativeai as genai

def askbot(user_quiston):    
    user_quiston = user_quiston.replace('/ask', '')
    if user_quiston:
        load_dotenv()
        genai.configure(api_key=os.getenv('GGEMINI_API_KEY'))

        generation_config = {
        "temperature": 0.3,
        "top_p": 1,
        "top_k": 1,
        "max_output_tokens": 2048,
        }

        safety_settings = [
        {
            "category": "HARM_CATEGORY_HARASSMENT",
            "threshold": "BLOCK_MEDIUM_AND_ABOVE"
        },
        {
            "category": "HARM_CATEGORY_HATE_SPEECH",
            "threshold": "BLOCK_MEDIUM_AND_ABOVE"
        },
        {
            "category": "HARM_CATEGORY_SEXUALLY_EXPLICIT",
            "threshold": "BLOCK_MEDIUM_AND_ABOVE"
        },
        {
            "category": "HARM_CATEGORY_DANGEROUS_CONTENT",
            "threshold": "BLOCK_MEDIUM_AND_ABOVE"
        },
        ]

        model = genai.GenerativeModel(model_name="gemini-1.0-pro",
                                    generation_config=generation_config,
                                    safety_settings=safety_settings)

        convo = model.start_chat(history=[
        ])
        try:
            convo.send_message(user_quiston)
            return convo.last.text
        except:
            return 'Я искуственный интелект и не могу отвечать на такой тип вопросов.'
    else:
        return 'После /ask напишите свой вопрос.'

def spehere():
    load_dotenv()   
    genai.configure(api_key=os.getenv('GGEMINI_API_KEY'))
    model = genai.GenerativeModel('gemini-pro')
    user_question = "Вы профессиональный финансист и экономист.Не говорите, что вы профессиональный финансист и экономист. Мне нужны 3 перспективные сектора для инвестиций. Сохраняйте профессионализм и читабельно напишите текст, в какие сферы лучше инвестировать. Кратко опишите каждую сферу. Не говорите, что вы профессиональный экономист и финансист."
    response = model.generate_content(user_question)
    if user_question:
        return response.text