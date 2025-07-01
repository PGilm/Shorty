# Welcome to Shorty

A flask application

https://www.freecodecamp.org/news/how-to-implement-two-factor-authentication-in-your-flask-app/

pip install Flask Flask-Login Flask-Bcrypt Flask-WTF FLask-Migrate Flask-SQLAlchemy pyotp qrcode python-decouple


How to Run the Completed App for the First Time, use the command:

    flask db init

To migrate the database changes, use the command:

    flask db migrate

To apply the migrations, use the command:

    flask db upgrade

To run the application, use the command:

    python manage.py run


gunicorn -b 0.0.0.0:5004 -w 4 -k gevent 'app:app'

