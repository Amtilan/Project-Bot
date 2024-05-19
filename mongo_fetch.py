from pymongo import MongoClient
import os
from dotenv import load_dotenv
import json
import asyncio

async def update_and_save_data():
    load_dotenv()
    client = MongoClient(os.getenv('MONGO_DB'))
    db = client['company_financials']
    collection = db['data']

    results = collection.find({'weeks': {'$gt': 15}}, {'_id': 0})
    results_list = [result for result in results]

    with open('results.json', 'w') as file:
        pretty_json = json.dumps(results_list, indent=4)
        file.write(pretty_json)
        
asyncio.run(update_and_save_data())