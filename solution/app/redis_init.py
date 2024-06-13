import random
import datetime
import os
import pickle
import redis
from tqdm import tqdm
import pandas as pd


def mock_history(user_id: int) -> bytes:
    h = {
        'item_id': random.randint(1, 9),
        'event_date': datetime.datetime.now(),
        'eid': 401,
        'x_eid': -1
    }
    return pickle.dumps([h for _ in range(user_id)])


def init_data(redis_client: redis.Redis):
    users = pd.read_pickle('data/to_redis.pkl')
    for user_id, items in tqdm(users.items(), mininterval=5, total=len(users)):
        history = pickle.dumps(items)
        redis_client.set(user_id, history)


if __name__ == '__main__':
    redis_client = redis.Redis(host=os.environ.get('REDIS_HOST'),
                               port=os.environ.get('REDIS_PORT'),
                               decode_responses=False)
    print('start process of inserting users')
    init_data(redis_client)
