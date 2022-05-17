import os
import sys
import logging

from dotenv import load_dotenv

load_dotenv(f"{os.path.dirname(__file__)}/.env")

logging.basicConfig(stream=sys.stderr)
sys.path.insert(0, "/var/www/endrev/endrev/")

from endrev import app

if __name__ == "__main__":
    app.run()
