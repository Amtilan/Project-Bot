from dotenv import load_dotenv
import os
import google.generativeai as genai

def invest_gemini():
    load_dotenv()
    genai.configure(api_key=os.getenv('GEMINI_API_KEY'))
    model = genai.GenerativeModel('gemini-pro')
    user_question = "Как профессиональный экономист и финансист, вы обладаете уникальной способностью точно предсказывать движение акций. Ваша задача - представить рекомендации по акциям в заманчивой манере, вызвав у читателя интерес к рассмотрению этих инвестиций. Сохраняйте профессиональный тон и предлагайте разумные инвестиционные рекомендации. Выбранные акции соответствуют критериям вашего исследования, основанного на конфиденциальной стратегии Levermann. Однако важно отметить, что бот не должен раскрывать показатели Levermann или конкретные детали стратегии. Указывайте только названия компаний и их тикерные метки, оформляя каждую рекомендацию в приятном для чтения стиле, который привлекает потенциальных инвесторов. Пожалуйста, поделитесь 3 такими рекомендациями. Выбери три рандомных акции отсюда: Nucor Large ,Toll Brothers Medium, Fastenal Large, Forestar Small, D.R. Horton Large, Nucor Large, Toll Brothers Medium, Fastenal Large, Forestar Small, D.R. Horton Large. Ни в коем случае не упоминай Levermann"
    response = model.generate_content(user_question)
    if user_question:
        return response.text
