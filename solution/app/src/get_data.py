from postgres_init import Items
import pickle


def set_history_to_user(redis_client, user_id, history):
    redis_client.set(user_id, pickle.dumps(history))


def create_new_user(redis_client):
    user_id = redis_client.dbsize() + 1
    set_history_to_user(redis_client, user_id, [])
    return user_id


def get_item_info(db, item_id):
    item = db.get_or_404(Items, item_id,
                         description=f'Item с индексом {item_id} не найден.')
    return {
        'item_id': item.id,
        'title': item.title,
        'description': item.description,
        'start_date': item.starttime
    }


def get_user_history(user_id, redis_client):
    obj = redis_client.get(user_id)
    if obj is None:
        return None
    return pickle.loads(redis_client.get(user_id))


def mock_recommendations():
    return list(range(1, 10))


def get_model_predictions(history):
    return mock_recommendations()


def get_recommendations(history, db):
    preds = get_model_predictions(history)
    return [get_item_info(db, item_id) for item_id in preds]
