from flask import Flask
from flask_login import LoginManager
from flask_migrate import Migrate
from flask_sqlalchemy import SQLAlchemy

from app.config import APP_SECRET_KEY, DATABASE_URI

app = Flask(__name__)
app.url_map.strict_slashes = False

app.jinja_env.trim_blocks = True
app.jinja_env.lstrip_blocks = True
app.secret_key = APP_SECRET_KEY

app.config["SQLALCHEMY_DATABASE_URI"] = DATABASE_URI
db = SQLAlchemy(app)
migrate = Migrate(app, db, render_as_batch=True)

login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = "login"

from api import sylvia_api, zelda_api

from app.hidden.hidden import hidden_pages
from app.home import home
from app.rb.rb import rb

app.register_blueprint(home)
app.register_blueprint(hidden_pages)
app.register_blueprint(rb, url_prefix="/rb")
app.register_blueprint(sylvia_api, url_prefix="/sylvia")
app.register_blueprint(zelda_api, url_prefix="/zelda")

if __name__ == "__main__":
    app.run(host="0.0.0.0")
