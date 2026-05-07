from threading import Thread

from api import run_flask
from client import run_bot

if __name__ == "__main__":
    flask_thread = Thread(target=run_flask, daemon=True)
    flask_thread.start()

    run_bot()
