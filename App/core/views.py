from flask import Flask, json, redirect, url_for, render_template, request, session, flash, Blueprint, jsonify

from flask_login import login_required

from flask_session import Session

from datetime import datetime, timedelta

core_bp = Blueprint("core", __name__)

from .. import app # refact

import re  # for the RegEx
from bs4 import BeautifulSoup
import pandas as pd

from App.static import shortyFunc as sf

# import _config_  # hidden in .venv\lib\python\site-packages

app.secret_key = 123456789123456789  # _config_.SECRET_KEY # "123456789"

app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"
Session(app)

app.permanent_session_lifetime = timedelta(days=15)


@core_bp.route("/") # base or no route renders user-home or new-login 
# @login_required
def none():
    if "user" in session:
            return render_template(
                "core/home.html",
                name = session["user"]
            )
    else:
        flash("Hello! This flash message because this is your first time?", "info")
        return redirect(url_for("accounts.login"))

@core_bp.route("/home/")
@core_bp.route("/home/<name>")
@login_required
def home(name = None):
    return render_template(
        "core/home.html",
        name = name # session["user"] # user
    )

# @core_bp.route("/login/", methods=["POST", "GET"])
# def login():
#     if request.method == "POST":
#         session.permanent = True
#         session["user"] = request.form["nm"]
#         return redirect(url_for("core.home"))
#     else:
#         return render_template("accounts/login.html")

# @core_bp.route("/logout/")
# def logout():
#     if "user" in session:
#         session.clear()
#         return redirect(url_for("accounts.login"))
#     else:
#         return redirect(url_for("core.about"))

@core_bp.route("/about/")
def about():
    return render_template("core/about.html")

@core_bp.route("/contact/")
def contact():
    return render_template("core/contact.html")

@core_bp.route("/shortytable/", methods=['GET', 'POST'])
@core_bp.route("/shortytable/<table_html>")
def shortytable(table_html=None):
    if request.method == 'POST':
        sf.get_ShortyTable()

    if "table_html" in session:
        return render_template(
            "core/shortytable.html",
            table_html = session["table_html"]
        )
    return render_template(
        'core/shortytable.html',
        table_html = None
        )

@core_bp.route("/shortyjson/", methods=['GET', 'POST'])
@core_bp.route("/shortyjson/<table_json>")
def shortyjson(table_json=None):
    if request.method == 'POST':
        sf.get_ShortyJson()

    if "table_json" in session:
        return render_template(
            "core/shortyjson.html",
            table_json = session["table_json"]
        )
    return render_template(
        'core/shortyjson.html',
        table_json = None
        )

@core_bp.route('/save', methods=['POST'])
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
@core_bp.route("/api/data/")
def get_data():
    return app.send_static_file("data.json")

@core_bp.route("/hello/")
@core_bp.route("/hello/<name>")
def hello_there(name = None):
    return render_template(
        "core/hello_there.html",
        name=name,
        date=datetime.now()
    )

@core_bp.route("/oldhello/<name>")
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
    # "http://127.0.0.1:5000/hello/VSCode"
    return content

if __name__ == '__main__':
    port = sf.get_port()
    app.run(host='0.0.0.0', debug=True, port=port)
