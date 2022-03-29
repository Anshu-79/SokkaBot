from flask import Flask
from threading import Thread
from os import environ, system
from logging import getLogger

system("cls||clear")

# Edit these to your liking...
write_to_console = False
text = "Hello! I'm SokkaBot, a Discord bot made with disnake."

if not write_to_console:
    getLogger("werkzeug").disabled = True
    environ["WERKZEUG_RUN_MAIN"] = "true"

app = Flask("")


@app.route("/")
def home():
    return text


def run():
    app.run(host="0.0.0.0", port=8080)


def keep_alive():
    t = Thread(target=run)
    t.start()
