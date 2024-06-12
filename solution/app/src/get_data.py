from postgres_init import Items
import pickle
import pandas as pd

from typing import List, Dict, Any
import redis
from flask_sqlalchemy import SQLAlchemy


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
    item = db.get_or_404(Items, item_id,
                         description=f'Item с индексом {item_id} не найден.')
    return {
        'item_id': item.id,
        'title': item.title,
        'category': get_category_by_id(item.category_id),
        'starttime': item.starttime.strftime("%d/%m/%Y, %H:%M:%S")
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
    return mock_recommendations()


def get_recommendations(db: SQLAlchemy,
                        history: List[Dict]) -> List[Dict[str, Any]]:
    preds = get_model_predictions(history)
    return [get_item_info(db, item_id) for item_id in preds]
