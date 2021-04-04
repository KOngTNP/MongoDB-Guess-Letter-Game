import os
import redis

from flask import Flask
from flask import render_template
from pymongo import MongoClient

application = Flask(__name__)

mongoClient = MongoClient(
    'mongodb://' + os.environ['MONGODB_USERNAME'] + ':' + os.environ['MONGODB_PASSWORD'] + '@' + os.environ[
        'MONGODB_HOSTNAME'] + ':27017/' + os.environ['MONGODB_AUTHDB'])
db = mongoClient[os.environ['MONGODB_DATABASE']]

redisClient = redis.Redis(host=os.environ.get("REDIS_HOST", "localhost"), port=os.environ.get("REDIS_PORT", 6379),
                          db=os.environ.get("REDIS_DB", 0))


def insert():
    db.guessing_game.insert_one(
        {"guess": ['-', '-', '-', '-'], 
        "show": ['-', '-', '-', '-'], 
        "secret": ['', '', '', ''], 
        "index": 0,
        "index2": 0, 
        "num": 0}
    )

@application.route('/')
def index():
    doc = db.guessing_game.find_one()
    if doc is None:
        insert()
    return render_template("index.html")


@application.route('/get_start')
def get_ready():
    doc = db.guessing_game.find_one()
    if doc is None:
        insert()
    body = "<h1>Get Start</h1>"
    body += "<h3>Pick 4 Letter</h3>"

    for i in range(4):
        body += "        "
        body += doc["show"][i]
        
    body += '<h3><a href="/A_letter" class="button">Letter: A</a></h3>'
    body += '<h3><a href="/B_letter" class="button">Letter: B</a></h3>'
    body += '<h3><a href="/C_letter" class="button">Letter: C</a></h3>'
    body += '<h3><a href="/D_letter" class="button">Letter: D</a></h3>'

    body += '<button><a href="/">Back to home</a></button>'
    body += '<button><a href="/reset">Reset</a></button>'
    if doc["index"] >= 4:
        body += '<button><a href="/game_started">Game Start</a></button>'
    return body


def updateSecret(x, y):
    doc = db.guessing_game

    if y["index"] > 3:
        doc.update_one({}, {"$set": {"index": 0}})

    if y["index"] == 0:
        doc.update_one({}, {"$set": {"show.0": "X"}})
        doc.update_one({}, {"$set": {"secret.0": x}})

    elif y["index"] == 1:
        doc.update_one({}, {"$set": {"show.1": "X"}})
        doc.update_one({}, {"$set": {"secret.1": x}})

    elif y["index"] == 2:
        doc.update_one({}, {"$set": {"show.2": "X"}})
        doc.update_one({}, {"$set": {"secret.2": x}})

    elif y["index"] == 3:
        doc.update_one({}, {"$set": {"show.3": "X"}})
        doc.update_one({}, {"$set": {"secret.3": x}})

    doc.update_one({}, {"$set": {"index": y["index"] + 1}})


@application.route('/game_started')
def game_started():
    doc = db.guessing_game.find_one()
    body = "<h1>Game Start</h1>"
    body += "<h3>Guess the letter</h3>"

    for i in range(4):
        body += "    "
        body += doc["guess"][i]
    body += "<h1></h1>"
    body += f'Number of click: {doc["num"]}'
    body += '<h3><a href="/A_guess" class="button">Letter: A</a></h3>'
    body += '<h3><a href="/B_guess" class="button">Letter: B</a></h3>'
    body += '<h3><a href="/C_guess" class="button">Letter: C</a></h3>'
    body += '<h3><a href="/D_guess" class="button">Letter: D</a></h3>'

    if doc["guess"][3] != "-":
        num = doc["num"]
        return render_template("win.html", num=num)
    return body


@application.route('/A_letter')
def A_letter():
    doc = db.guessing_game.find_one()
    updateSecret("A", doc)
    return get_ready()
@application.route('/B_letter')
def B_letter():
    doc = db.guessing_game.find_one()
    updateSecret("B", doc)
    return get_ready()
@application.route('/C_letter')
def C_letter():
    doc = db.guessing_game.find_one()
    updateSecret("C", doc)
    return get_ready()
@application.route('/D_letter')
def D_letter():
    doc = db.guessing_game.find_one()
    updateSecret("D", doc)
    return get_ready()


def guessSecret(x, y):
    if y["guess"][3] != "-":
        return

    doc = db.guessing_game

    def doc_update():
        doc.update_one({}, {"$set": {"num": y["num"] + 1}})
        doc.update_one({}, {"$set": {"index2": y["index2"] + 1}})

    if y["index2"] > 3:
        doc.update_one({}, {"$set": {"index2": 0}})

    if y["index2"] == 0 and x == y["secret"][0]:
        doc_update()
        doc.update_one({}, {"$set": {"guess.0": x}})
        return

    elif y["index2"] == 1 and x == y["secret"][1]:
        doc_update()
        doc.update_one({}, {"$set": {"guess.1": x}})
        return

    elif y["index2"] == 2 and x == y["secret"][2]:
        doc_update()
        doc.update_one({}, {"$set": {"guess.2": x}})
        return

    elif y["index2"] == 3 and x == y["secret"][3]:
        doc_update()
        doc.update_one({}, {"$set": {"guess.3": x}})
        return

    else:
        doc.update_one({}, {"$set": {"num": y["num"] + 1}})
        return


@application.route('/A_guess')
def A_guess():
    doc = db.guessing_game.find_one()
    guessSecret("A", doc)
    return game_started()

@application.route('/B_guess')
def B_guess():
    doc = db.guessing_game.find_one()
    guessSecret("B", doc)
    return game_started()

@application.route('/C_guess')
def C_guess():
    doc = db.guessing_game.find_one()
    guessSecret("C", doc)
    return game_started()

@application.route('/D_guess')
def D_guess():
    doc = db.guessing_game.find_one()
    guessSecret("D", doc)
    return game_started()

@application.route('/reset')
def reset():
    doc = db.guessing_game

    doc.update_one({}, {"$set": {"guess.0": "-"}})
    doc.update_one({}, {"$set": {"guess.1": "-"}})
    doc.update_one({}, {"$set": {"guess.2": "-"}})
    doc.update_one({}, {"$set": {"guess.3": "-"}})

    doc.update_one({}, {"$set": {"show.0": "-"}})
    doc.update_one({}, {"$set": {"show.1": "-"}})
    doc.update_one({}, {"$set": {"show.2": "-"}})
    doc.update_one({}, {"$set": {"show.3": "-"}})

    doc.update_one({}, {"$set": {"secret.0": ""}})
    doc.update_one({}, {"$set": {"secret.1": ""}})
    doc.update_one({}, {"$set": {"secret.2": ""}})
    doc.update_one({}, {"$set": {"secret.3": ""}})

    doc.update_one({}, {"$set": {"index": 0}})
    doc.update_one({}, {"$set": {"index2": 0}})
    doc.update_one({}, {"$set": {"num": 0}})

    return get_ready()


if __name__ == "__main__":
    ENVIRONMENT_DEBUG = os.environ.get("FLASK_DEBUG", True)
    ENVIRONMENT_PORT = os.environ.get("FLASK_PORT", 5000)
    application.run(host='0.0.0.0', port=ENVIRONMENT_PORT,
                    debug=ENVIRONMENT_DEBUG)
