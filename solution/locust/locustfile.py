from locust import HttpUser, SequentialTaskSet, task
import random

TEST_ITEM_IDS = [3, 7]  # TODO: SOME REAL IDS


class UserBehavior(SequentialTaskSet):
    @task
    def get_user(self):
        """Init session, get recommendations."""
        self.user_id = random.randint(1, 90)
        if random.random() < 0.75:
            self.client.post('/get_user',
                             data={'userId': self.user_id})
        else:
            self.client.post('/create_user')
        self.client.get('/index')

    @task
    def make_actions(self):
        """Make actions."""
        eid = 401
        x_eid = -1
        for i in range(5):
            item_id = random.choice(TEST_ITEM_IDS)
            self.client.post('/make_action',
                             data={'eid': eid,
                                   'x_eid': x_eid,
                                   'item_id': item_id})
        self.client.post('/update_recommendations')
        self.client.post('/change_user')


class WebsiteUser(HttpUser):
    tasks = [UserBehavior]
    host = 'http://flask-app:8000'
