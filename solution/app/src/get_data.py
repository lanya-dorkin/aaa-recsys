import os
from typing import List, Dict, Any
import pickle
from datetime import datetime
import pandas as pd
import requests
from flask_sqlalchemy import SQLAlchemy
import redis
from postgres_init import Items



categories_mapping: Dict[int, str] = pd.read_csv(
    'data/categories_mapping.csv',
    dtype={'category_id': int},
    index_col='category_id')\
        .to_dict()['category_name']


def get_category_by_id(category_id: int):
    return categories_mapping[category_id]


def set_history_to_user(redis_client: redis.Redis,
                        user_id: int,
                        history: List[Dict]):
    redis_client.set(user_id, pickle.dumps(history))


def create_new_user(redis_client: redis.Redis) -> int:
    user_id = redis_client.dbsize() + 1
    set_history_to_user(redis_client, user_id, [])
    return user_id


def get_item_info(db: SQLAlchemy, item_id: int) -> Dict[str, Any]:
    try:
        item = db.get(Items, item_id,
                            description=f'Item с индексом {item_id} не найден.')
    except:
        item = None

    if item is None:
        return {
            'item_id': item_id,
            'title': 'Не найден',
            'category': get_category_by_id(0),
            'starttime': datetime.now().strftime('%d/%m/%Y, %H:%M:%S')
        }
    return {
        'item_id': item.id,
        'title': item.title,
        'category': get_category_by_id(item.category_id),
        'starttime': item.starttime.strftime('%d/%m/%Y, %H:%M:%S')
    }


def get_user_history(user_id: int,
                     redis_client: redis.Redis) -> List[Dict[str, Any]]:
    obj = redis_client.get(user_id)
    if obj is None:
        return None
    return pickle.loads(redis_client.get(user_id))


def mock_recommendations():
    return list(range(1, 10))


def get_model_predictions(history: List[Dict[str, Any]]) -> List[int]:
    model_service_host = os.environ.get('MODEL_SERVICE_HOST')
    model_service_port = os.environ.get('MODEL_SERVICE_PORT')

    for item in history:
        item['event_date'] = item['event_date'].strftime('%Y/%m/%d, %H:%M:%S')

    if not model_service_host or not model_service_port:
        raise ValueError("Model service host or port is not set in environment variables")

    url = f"http://{model_service_host}:{model_service_port}/get_prediction"
    response = requests.post(url, json=history)

    if response.status_code != 200:
        raise Exception(f"Request to model service failed with status code {response.status_code}")

    response_json = response.json()
    predictions_str = response_json.get('predictions')

    if predictions_str is None:
        raise ValueError("'prediction' field is missing in the response")
    
    return [int(pred) for pred in predictions_str]


def get_recommendations(db: SQLAlchemy,
                        history: List[Dict]) -> List[Dict[str, Any]]:
    preds = get_model_predictions(history)
    return [get_item_info(db, item_id) for item_id in preds]
