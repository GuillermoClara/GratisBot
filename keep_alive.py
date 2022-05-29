from flask import Flask
from threading import Thread
import twitter

app = Flask('')


# Used to call the bot to check recent replies
@app.route('/')
def home():
    print('')
    return "Checking for replies!"


# Used to call the bot to post top courses
@app.route('/top')
def top():
    twitter.post_hot_topics('es')
    return "Posting new courses..."


# Used to call the bot to post discounts
@app.route('/discounts')
def discounts():
    twitter.post_discounts()
    return "Posting discounts..."


# Used for reply to user simulation
@app.route('/test')
def test():
    response = twitter.sim_tweet()
    return response


# Used for top courses simulation
@app.route('/toptest')
def toptest():
    twitter.sim_top('es')
    return 'Top test'


def run():
    app.run(host='0.0.0.0', port=8000)


def keep_alive():
    t = Thread(target=run)
    t.start()
