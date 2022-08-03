from flask import Flask
from threading import Thread
import twitter


app = Flask('')


@app.route('/')
def home():
    twitter.check_users_replies()
    return "Checking for replies!"


@app.route('/top')
def top():
    twitter.post_hot_topics('es')
    return "Posting new courses..."


@app.route('/discounts')
def discounts():
    twitter.post_discounts()
    return "Posting discounts..."


def run():
    app.run(host='0.0.0.0', port =8000)


def keep_alive():
    t = Thread(target=run)
    t.start()
