# Welcome to Shorty

A flask application

How to Run the Completed App for the First Time
Now that our application is ready, you can ﬁrst migrate the database, and then run the app. To initialize the database (create a migration repository), use the command:

    flask db init

To migrate the database changes, use the command:

    flask db migrate

To apply the migrations, use the command:

    flask db upgrade

To run the application, use the command:

    python manage.py run
