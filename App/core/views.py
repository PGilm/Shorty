from flask import Flask, json, redirect, url_for, render_template, request, session, flash, Blueprint, jsonify
from flask_login import login_required
from flask_session import Session

from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager, login_user, current_user, login_required

from datetime import datetime, timedelta

core_bp = Blueprint("core", __name__)

from .. import app # refact

import re  # for the RegEx
from bs4 import BeautifulSoup
import pandas as pd

from App.static import shortyFunc as sf


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
    if request.method == 'POST':
        session.clear # pop("user", None)
        return redirect(url_for("login"))
    if "user" in session:
        # user = session["user"]
        return render_template(
            "home.html",
            name = session["user"] # user
        )
    else:
        return redirect(url_for("login"))

@app.route("/login-old/", methods=["POST", "GET"])
def loginold():
    if request.method == "POST":
        session.permanent = True
        session["user"] = request.form["nm"]
        return redirect(url_for("home"))
    else:
        return render_template("loginold.html")

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        user = sf.User.query.filter_by(username=username).first()
        if user and sf.check_password_hash(user.password, password):
            login_user(user)
            session.permanent = True
            session["user"] = user
            return redirect(url_for('twofaverify'))
        else:
            flash('Invalid username or password.', 'danger')
    return render_template('login.html')

@app.route('/twofasetup', methods=['GET', 'POST'])
@login_required
def setup_2fa():
    if request.method == 'POST':
        secret = sf.generate_2fa_secret()
        current_user.two_factor_secret = secret
        db.session.commit()
        sf.generate_qr_code(secret, current_user.username)
        flash('Scan the QR code with your authenticator app.', 'info')
        return redirect(url_for('twofaverify'))
    return render_template('twofasetup.html')

@app.route('/twofaverify', methods=['GET', 'POST'])
@login_required
def verify_2fa():
    if request.method == 'POST':
        otp = request.form.get('otp')
        totp = sf.pyotp.TOTP(current_user.two_factor_secret)
        if totp.verify(otp):
            flash('2FA setup complete.', 'success')
            return redirect(url_for('home'))
        else:
            flash('Invalid OTP. Please try again.', 'danger')
    return render_template('twofaverify.html')

@core_bp.route("/about/")
def about():
    return render_template("core/about.html")

@core_bp.route("/contact/")
def contact():
    return render_template("core/contact.html")

@app.route("/shortytable/", methods=['GET', 'POST'])
@app.route("/shortytable/<table_html>")
@login_required
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

@app.route("/shortyjson/", methods=['GET', 'POST'])
@app.route("/shortyjson/<table_json>")
@login_required
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

@app.route('/save', methods=['POST'])
@login_required
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
