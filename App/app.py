import platform
from flask import Flask, json, redirect, url_for, render_template, request, session, flash, jsonify
from flask_session import Session

from datetime import datetime, timedelta

import re  # for the RegEx
from bs4 import BeautifulSoup
import pandas as pd

import get_port
import _config_  # hidden in .venv\lib\python\site-packages

app = Flask(__name__)
app.secret_key = _config_.secret_key # "123456789"

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
        file = request.files.get('file')
        if file and file.filename:
            try:
                html_content = file.read()
                soup = BeautifulSoup(html_content, 'html.parser')
                table = soup.find('table')
                if table:
                    # Check if the table has the class 'ShortyTable'
                    if 'ShortyTable' not in table.get('class', []):
                        # If not, set the class to 'ShortyTable'
                        table['class'] = table.get('class', []) + ['ShortyTable']
                    # Add a new column with buttons to each row
                    for row in table.find_all('tr'):
                        new_cell = soup.new_tag('td')
                        
                        copy_button = soup.new_tag('button', type='button', id='copy-button', **{'class': 'smbtn smbtn-copy'})
                        copy_button.string = 'Copy'
                        new_cell.append(copy_button)
                        
                        # new_cell.append(soup.new_tag('br'))
                        
                        edit_button = soup.new_tag('button', type='button', id='edit-button', **{'class': 'smbtn smbtn-edit'})
                        edit_button.string = 'Edit'
                        new_cell.append(edit_button)
                        
                        # new_cell.append(soup.new_tag('br'))
                        
                        delete_button = soup.new_tag('button', type='button', id='delete-button', **{'class': 'smbtn smbtn-delete'})
                        delete_button.string = 'Delete'
                        new_cell.append(delete_button)
                        
                        row.append(new_cell)
                    
                    # Assign the modified table HTML to session
                    while "table_html" in session:
                        session.pop("table_html", None)
                    session["table_html"] = str(table)
                    session["filenamehtml"] = file.filename
                else:
                    session["table_html"] = "No table found in the HTML file."
            except Exception as e:
                session["table_html"] = f"Error processing file: {e}"

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
        file = request.files.get('file')
        if file and file.filename:
            try:
                json_content = file.read()
                data = json.loads(json_content)
                # Convert JSON data to HTML table
                table_json = f'<table id="{file.filename}" class="ShortyTable">'
                if isinstance(data, list):
                    # Assuming the JSON data is a list of dictionaries
                    headers = data[0].keys()
                    table_json += '<thead><tr>'
                    for header in headers:
                        table_json += f'<th><div>{header}</div></th>' 
                    table_json += '<th><div>Actions</div></th></tr></thead><tbody>'
                    for row in data:
                        table_json += '<tr>'
                        for cell in row.values():
                            table_json += f'<td><div>{cell}</div></td>'
                        table_json += '''
                            <td>
                                <button type="button" id="copy-button" class="smbtn smbtn-copy">Copy</button>
                                <button type="button" id="edit-button" class="smbtn smbtn-edit">Edit</button>
                                <button type="button" id="delete-button" class="smbtn smbtn-delete">Delete</button>
                            </td>
                        '''
                        table_json += '</tr>'
                    table_json += '</tbody>'
                table_json += '</table>'
                
                while "table_json" in session:
                    session.pop("table_json", None)
                session["table_json"] = str(table_json)
                session["filenamejson"] = file.filename
                return render_template('shortyjson.html', table_json=session["table_json"])
            except Exception as e:
                session["table_json"] = f"Error processing JSON file: {e}"

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

    content = "Hello there, " + clean_name + "! It's " + formatted_now
    return content

if __name__ == '__main__':
    port = get_port()
    app.run(host='0.0.0.0', debug=True, port=port)
