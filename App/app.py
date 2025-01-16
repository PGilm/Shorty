from flask import Flask, url_for, render_template, redirect, flash
from datetime import datetime, timedelta

import re  # for the RegEx

app = Flask(__name__)
app.secret_key = "123456789"
app.permanent_session_lifetime = timedelta(days=5)

@app.route("/")
def none():
    flash("Hello! This flash message because this is your first time?", "info")
    return redirect(url_for("home"))

@app.route("/home/")
def home():
    return render_template("home.html")

@app.route("/about/")
def about():
    return render_template("about.html")

@app.route("/contact/")
def contact():
    return render_template("contact.html")

@app.route("/datatable/")
def datatable(datatable = None):
    return render_template(
        "datatable.html",
        datatable="data.json",
    )

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

    content = "Hello there, " + clean_name + "! It's " + formatted_now
    return content
