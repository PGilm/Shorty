# Welcome to Shorty

A flask application

pip install Flask Flask-Login Flask-Bcrypt Flask-WTF FLask-Migrate Flask-SQLAlchemy pyotp qrcode python-decouple

gunicorn -b 0.0.0.0:5004 -w 4 -k gevent 'app:app'



export SECRET_KEvzfdkjshfhjsdfdskfdsfdcbsjdkfdsdf
export DEBUG=True
export APP_SETTINGS=config.DevelopmentConfig
export DATABASE_URLzsqlite:///db.sqlite
export FLASK_APP=src
export FLASK_DEBUG=1
export APP_NAME="Flask User Authentication App”
