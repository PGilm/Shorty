from flask import Flask, redirect, url_for, render_template, request, session, flash
from datetime import datetime, timedelta

import re  # for the RegEx
from bs4 import BeautifulSoup
import pandas as pd

app = Flask(__name__)
app.secret_key = "123456789"
app.permanent_session_lifetime = timedelta(minutes=15)

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
    # elif request.method == 'GET':
    #     return render_template(url_for('about'))
    #
    if "user" in session:
        user = session["user"]
        return render_template(
            "home.html",
            name = session["user"]
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
        session.pop("user", None)
        return redirect(url_for("login"))
    else:
        return redirect(url_for("about"))

@app.route("/about/")
def about():
    return render_template("about.html")

@app.route("/contact/")
def contact():
    return render_template("contact.html")

@app.route("/datatable/", methods=['GET', 'POST'])
def datatable():
    if request.method == 'POST':
        session.permanent = True
        file = request.files.get('file')
        if file and file.filename:
            try:
                html_content = file.read()
                soup = BeautifulSoup(html_content, 'html.parser')
                table = soup.find('table')
                if table:
                    if "table_html" in session:
                        session.pop("table_html", None)
                    session.permanent = True
                    session["table_html"] = str(table)
                else:
                    session["table_html"] = "No table found in the HTML file."
            except Exception as e:
                session["table_html"] = f"Error processing file: {e}"

    table_html = session.get("table_html")
    return render_template('datatable.html', table_html=table_html)

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

if __name__ == '__main__':
    app.run(debug=True)
    