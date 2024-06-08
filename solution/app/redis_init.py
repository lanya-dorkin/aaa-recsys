import redis
import random
import datetime
import os
import pickle


def mock_history(user_id):
    h = {
        'item_id': random.randint(1, 9),
        'event_date': datetime.datetime.now(),
        'eid': 401,
        'x_eid': -1
    }
    return pickle.dumps([h for _ in range(user_id)])


def init_data(redis_client):
    # TODO: Read real data?
    for user_id in range(1, 100):
        history = mock_history(user_id)
        redis_client.set(user_id, history)


if __name__ == '__main__':
    redis_client = redis.Redis(host=os.environ.get('REDIS_HOST'),
                               port=os.environ.get('REDIS_PORT'),
                               decode_responses=False)
    init_data(redis_client)
