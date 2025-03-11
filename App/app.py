from flask import Flask, json, redirect, url_for, render_template, request, session, flash, jsonify
from flask_session import Session

from datetime import datetime, timedelta

import re  # for the RegEx
from bs4 import BeautifulSoup
import pandas as pd

import static.shortyFunc as sf
import _config_  # hidden in .venv\lib\python\site-packages

app = Flask(__name__)
app.secret_key = _config_.SECRET_KEY # "123456789"

app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"
Session(app)

app.permanent_session_lifetime = timedelta(days=15)

@app.route("/")
def none():
    if "user" in session:
            user = session["user"]
            return render_template(
                "home.html",
                name = session["user"]
            )
    else:
        flash("Hello! This flash message because this is your first time?", "info")
        return redirect(url_for("login"))

@app.route("/home/")
@app.route("/home/<name>")
def home(name = None):
    if request.method == 'POST':
        session.pop("user", None)
        return redirect(url_for("login"))
    if "user" in session:
        user = session["user"]
        return render_template(
            "home.html",
            name = user
        )
    else:
        return redirect(url_for("login"))

@app.route("/login/", methods=["POST", "GET"])
def login():
    if request.method == "POST":
        session.permanent = True
        session["user"] = request.form["nm"]
        return redirect(url_for("home"))
    else:
        return render_template("login.html")

@app.route("/logout/")
def logout():
    if "user" in session:
        session.clear()
        return redirect(url_for("login"))
    else:
        return redirect(url_for("about"))

@app.route("/about/")
def about():
    return render_template("about.html")

@app.route("/contact/")
def contact():
    return render_template("contact.html")

@app.route("/shortytable/", methods=['GET', 'POST'])
@app.route("/shortytable/<table_html>")
def shortytable(table_html=None):
    if request.method == 'POST':
        sf.get_ShortyTable()

    if "table_html" in session:
        return render_template(
            "shortytable.html",
            table_html = session["table_html"]
        )
    return render_template(
        'shortytable.html',
        table_html = None
        )

@app.route("/shortyjson/", methods=['GET', 'POST'])
@app.route("/shortyjson/<table_json>")
def shortyjson(table_json=None):
    if request.method == 'POST':
        sf.get_ShortyJson()

    if "table_json" in session:
        return render_template(
            "shortyjson.html",
            table_json = session["table_json"]
        )
    return render_template(
        'shortyjson.html',
        table_json = None
        )

@app.route('/save', methods=['POST'])
def save():
    data = request.get_json()
    updated_html = data.get('html')
    filename = session.get('filename', 'updated_file.html')
    try:
        with open(filename, 'w') as file:
            file.write(updated_html)
        return jsonify({'message': 'File saved successfully'})
    except Exception as e:
        return jsonify({'message': f'Error saving file: {e}'})

# For Demo purpose
@app.route("/api/data/")
def get_data():
    return app.send_static_file("data.json")

@app.route("/hello/")
@app.route("/hello/<name>")
def hello_there(name = None):
    return render_template(
        "hello_there.html",
        name=name,
        date=datetime.now()
    )

@app.route("/oldhello/<name>")
def oldhello_there(name):
    now = datetime.now()
    formatted_now = now.strftime("%A, %b %d, %y at %X")

    # Filter the name argument to letters only using regular expressions. 
    # URL arguments can contain arbitrary text, so we restrict to safe 
    # characters only.
    match_object = re.match("[a-zA-Z]+", name)

    if match_object:
        clean_name = match_object.group(0)
    else:
        clean_name = "Friend"

    content = "Hello there, " + clean_name + "!! It's " + formatted_now
    return content

if __name__ == '__main__':
    port = sf.get_port()
    app.run(host='0.0.0.0', debug=True, port=port)
