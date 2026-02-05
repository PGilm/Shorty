from decouple import config
from flask import Flask
import os
from flask_bcrypt import Bcrypt
from flask_migrate import Migrate
from flask_sqlalchemy import SQLAlchemy
from flask_session import Session

from flask_login import LoginManager # Add this line
from datetime import timedelta

app = Flask(__name__)
app.config.from_object(config("APP_SETTINGS"))

# Ensure session cookie works predictably behind proxies/load-balancers.
# Use Lax so top-level navigations (form submits) send the cookie; in
# cross-site setups set to 'None' and enable `SESSION_COOKIE_SECURE`.
app.config.setdefault('SESSION_COOKIE_SAMESITE', 'Lax')
if os.environ.get('FORCE_SECURE_COOKIES') == '1':
    app.config['SESSION_COOKIE_SECURE'] = True

# If the app is behind a reverse proxy (nginx/ALB) the ProxyFix ensures
# Flask sees the original host and scheme so cookies and redirects are
# generated correctly. Enable via environment when appropriate.
if os.environ.get('ENABLE_PROXYFIX', '1') == '1':
    try:
        from werkzeug.middleware.proxy_fix import ProxyFix
        app.wsgi_app = ProxyFix(app.wsgi_app, x_for=1, x_proto=1, x_host=1)
    except Exception:
        app.logger.warning('ProxyFix not applied; werkzeug may be missing')

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
    from flask import jsonify, session
    from flask_login import current_user
    import os
    base = '/Users/pg/proj/Shorty/-ShortyTables'
    # prefer authenticated user's folder, fall back to session user string
    username = None
    try:
        if current_user and getattr(current_user, 'is_authenticated', False):
            username = getattr(current_user, 'username', None)
    except Exception:
        username = None
    if not username:
        su = session.get('user')
        if isinstance(su, str):
            username = su
    folder = os.path.join(base, username) if username else base
    try:
        os.makedirs(folder, exist_ok=True)
        files = [f for f in os.listdir(folder) if f.endswith('.html')]
        return jsonify(files)
    except Exception as e:
        return jsonify({'error': str(e)})

@app.route('/list_json')
def list_json():
    from flask import jsonify, session
    from flask_login import current_user
    import os
    from flask import request as _flask_request
    base = '/Users/pg/proj/Shorty/-ShortyTables'
    username = None
    try:
        if current_user and getattr(current_user, 'is_authenticated', False):
            username = getattr(current_user, 'username', None)
    except Exception:
        username = None
    if not username:
        su = session.get('user')
        if isinstance(su, str):
            username = su
    folder = os.path.join(base, username) if username else base
    try:
        # Log request for remote debugging
        app.logger.info(f"list_json called from {_flask_request.remote_addr}; folder={folder}")
        os.makedirs(folder, exist_ok=True)
        files = [f for f in os.listdir(folder) if f.endswith('.json')]
        return jsonify(files)
    except Exception as e:
        app.logger.exception("Error in list_json")
        return jsonify({'error': str(e)})

from App.accounts.models import User

@login_manager.user_loader
def load_user(user_id):
    return User.query.filter(User.id == int(user_id)).first()
