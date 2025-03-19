from decouple import config
from flask import Flask
from flask_bcrypt import Bcrypt
from flask_migrate import Migrate
from flask_sqlalchemy import SQLAlchemy

from flask_login import LoginManager # Add this line

app = Flask(__name__)
app.config.from_object(config("APP_SETTINGS"))

login_manager = LoginManager() # Add this line
login_manager.init_app(app) # Add this line

login_manager.login_view = "accounts.login"
login_manager.login_message_category = "danger"

bcrypt = Bcrypt(app)
db = SQLAlchemy(app)
migrate = Migrate(app, db)

# Registering blueprints
from App.accounts.views import accounts_bp
from App.core.views import core_bp

app.register_blueprint(accounts_bp)
app.register_blueprint(core_bp)

from App.accounts.models import User

@login_manager.user_loader
def load_user(user_id):
    return User.query.filter(User.id == int(user_id)).first()
