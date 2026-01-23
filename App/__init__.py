from decouple import config
from flask import Flask
from flask_bcrypt import Bcrypt
from flask_migrate import Migrate
from flask_sqlalchemy import SQLAlchemy
from flask_session import Session

from flask_login import LoginManager # Add this line
from datetime import timedelta

app = Flask(__name__)
app.config.from_object(config("APP_SETTINGS"))

login_manager = LoginManager() # Add this line
login_manager.init_app(app) # Add this line

login_manager.login_view = "accounts.login"
login_manager.login_message_category = "danger"

app.secret_key = config("SECRET_KEY")

app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"
Session(app)

app.permanent_session_lifetime = timedelta(days=15)

bcrypt = Bcrypt(app)
db = SQLAlchemy(app)
migrate = Migrate(app, db)

# Registering blueprints
from App.accounts.views import accounts_bp
from App.core.views import core_bp

app.register_blueprint(accounts_bp)
app.register_blueprint(core_bp)

@app.route('/list_tables')
def list_tables():
    from flask import jsonify
    import os
    folder = '/Users/pg/proj/Shorty/-ShortyTables'
    try:
        files = [f for f in os.listdir(folder) if f.endswith('.html')]
        return jsonify(files)
    except Exception as e:
        return jsonify({'error': str(e)})

@app.route('/list_json')
def list_json():
    from flask import jsonify
    import os
    folder = '/Users/pg/proj/Shorty/-ShortyTables'
    try:
        files = [f for f in os.listdir(folder) if f.endswith('.json')]
        return jsonify(files)
    except Exception as e:
        return jsonify({'error': str(e)})

from App.accounts.models import User

@login_manager.user_loader
def load_user(user_id):
    return User.query.filter(User.id == int(user_id)).first()
