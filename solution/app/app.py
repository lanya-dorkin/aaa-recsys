from flask import Flask, render_template, request, redirect, url_for, session
from flask_sqlalchemy import SQLAlchemy
import datetime
import os
from src.get_data import get_recommendations, get_user_history, create_new_user
from src.get_data import set_history_to_user
from config import DB_ADDRESS
import redis

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = DB_ADDRESS
app.secret_key = os.environ.get('SECRET_KEY')
db = SQLAlchemy(app)
redis_client = redis.Redis(host=os.environ.get('REDIS_HOST'),
                           port=os.environ.get('REDIS_PORT'),
                           decode_responses=False)


@app.route('/index')
@app.route('/')
def index():
    user_id = session.get('user_id')
    recommendations = session.get('recommendations', [])
    return render_template('index.html',
                           user_id=user_id,
                           recommendations=recommendations)


@app.route('/get_user', methods=['POST'])
def get_user():
    user_id = int(request.form['userId'])
    history = get_user_history(user_id, redis_client)
    if history is None:
        return redirect(url_for('index'))
    session['history'] = history
    recommendations = get_recommendations(session['history'], db)
    session['user_id'] = user_id
    session['recommendations'] = recommendations
    return redirect(url_for('index'))


@app.route('/create_user', methods=['POST'])
def create_user():
    user_id = create_new_user(redis_client)
    recommendations = get_recommendations([], db)
    session['user_id'] = user_id
    session['history'] = []
    session['recommendations'] = recommendations
    return redirect(url_for('index'))


@app.route('/make_action', methods=['POST'])
def make_action():
    eid = request.form.get('eid')
    x_eid = request.form.get('x_eid')
    item_id = request.form.get('item_id')
    event_date = datetime.datetime.now()
    session['history'].append({
        'item_id': item_id,
        'event_date': event_date,
        'eid': eid,
        'x_eid': x_eid
    })
    if not session.modified:
        session.modified = True
    return redirect(url_for('index'))


@app.route('/update_recommendations', methods=['POST'])
def update_recommendations():
    recommendations = get_recommendations(session['history'], db)
    session['recommendations'] = recommendations
    return redirect(url_for('index'))


@app.route('/change_user', methods=['POST'])
def change_user():
    set_history_to_user(redis_client,
                        session['user_id'],
                        session['history'])
    session['user_id'] = None
    session['recommendations'] = None
    session['history'] = None

    return redirect(url_for('index'))


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=os.environ['FLASK_PORT'], debug=True)
