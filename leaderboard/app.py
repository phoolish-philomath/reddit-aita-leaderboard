from flask import Flask, render_template
from flask_socketio import SocketIO, emit
import redis
import arrow
import threading
import os

NUM_ROWS_TO_DISPLAY = 10

app = Flask(__name__)
app.config['REDIS_HOST'] = os.getenv('REDIS_HOST', 'localhost')
app.config['REDIS_PORT'] = os.getenv('REDIS_PORT', 6379)
socketio = SocketIO(app)

def connect_db():
    r = redis.Redis(host=app.config['REDIS_HOST'], port=app.config['REDIS_PORT'])
    connected = False
    while not connected:
        try:
            r.ping()
        except Exception as e:
            print(e)
            print('Failed to connect. Trying again...')
        else:
            print('Connection successful!')
            connected = True
    return r

r = connect_db()
pubsub = r.pubsub()
pubsub.subscribe('aita_comment_streams.yta')

def check_leaderboard_updates():
    for msg in pubsub.listen():
        print(msg)
        if msg["type"] == "message":
            socketio.emit('leaderboard_update', {
                'top_submissions': get_top_submissions(NUM_ROWS_TO_DISPLAY),
                'update_time': arrow.utcnow().format('YYYY-MM-DD HH:mm:ss UTC') 
                })

thread = threading.Thread(target=check_leaderboard_updates) 

def get_top_submissions(n):
    top_submission_ids_with_scores = r.zrevrange('aita_leaderboard', 0, n - 1, withscores=True)
    top_submissions = [build_submission_info(sub[0], i + 1) for i, sub in enumerate(top_submission_ids_with_scores)]
    return top_submissions

def build_submission_info(submission_id, rank):
    submission_record = r.hgetall(submission_id)
    return {
            "title": submission_record[b"title"].decode("utf-8"),
            "url": "https://www.reddit.com" + submission_record[b"url"].decode("utf-8"),
            "rank": rank
           }
    
@app.route('/')
def index():
    print('homepage!')
    timestamp_string = arrow.utcnow().format('YYYY-MM-DD HH:mm:ss UTC')
    return render_template('index.html', top_submissions=get_top_submissions(NUM_ROWS_TO_DISPLAY), current_time=timestamp_string)


@socketio.on('connect')
def test_connect():
    print('connecting!')
    if not thread.is_alive():
        print('starting thread')
        thread.start()

@socketio.on('disconnect')
def test_disconnect():
    print('disconnecting!')
    if thread.is_alive():
        print('stopping thread')
        thread.join()
        
if __name__ == '__main__':
    socketio.run(app, host='0.0.0.0')
