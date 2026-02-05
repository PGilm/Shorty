from flask import Flask, json, redirect, url_for, render_template, request, session, flash, Blueprint, jsonify
from flask_login import login_required
from flask_session import Session

from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager, login_user, current_user, login_required

from datetime import datetime, timedelta
import os
from bs4 import BeautifulSoup
from streamlit import html

core_bp = Blueprint("core", __name__)

from .. import app # refact

import re  # for the RegEx
from bs4 import BeautifulSoup
import pandas as pd

from App.static import shortyFunc as sf
from App.accounts.models import User
from App import bcrypt, db


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
            "core/home.html",
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
        user = User.query.filter_by(username=username).first()
        if user and bcrypt.check_password_hash(user.password, password):
            login_user(user)
            session.permanent = True
            session["user"] = user
            return redirect(url_for('verify_2fa'))
        else:
            flash('Invalid username or password.', 'danger')
    return render_template('accounts/login.html')

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
    if not current_user.two_factor_secret:
        return redirect(url_for('setup_2fa'))
    if request.method == 'POST':
        otp = request.form.get('otp')
        totp = sf.pyotp.TOTP(current_user.two_factor_secret)
        if totp.verify(otp):
            flash('2FA verification successful.', 'success')
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
        filename = request.form.get('filename')
        if filename:
            # load from file
            path = '/Users/pg/proj/Shorty/-ShortyTables/' + filename
            try:
                with open(path, 'r') as f:
                    html_content = f.read()
                soup = BeautifulSoup(html_content, 'html.parser')
                table = soup.find('table')
                if table:
                    if 'ShortyTable' not in table.get('class', []):
                        table['class'] = table.get('class', []) + ['ShortyTable']
                    for row in table.find_all('tr'):
                        new_cell = soup.new_tag('td')
                        copy_button = soup.new_tag('button', type='button', id='copy-button', **{'class': 'smbtn smbtn-copy'})
                        copy_button.string = 'Copy'
                        new_cell.append(copy_button)
                        edit_button = soup.new_tag('button', type='button', id='edit-button', **{'class': 'smbtn smbtn-edit'})
                        edit_button.string = 'Edit'
                        new_cell.append(edit_button)
                        delete_button = soup.new_tag('button', type='button', id='delete-button', **{'class': 'smbtn smbtn-delete'})
                        delete_button.string = 'Delete'
                        new_cell.append(delete_button)
                        row.append(new_cell)
                    session["table_html"] = str(table)
                    session["filenamehtml"] = path
                    #return render_template(
                        # 'core/shortytable.html', 
                        # table_html=session["table_html"])
                    return render_template(
                        'core/shortytable.html',
                        table_html=session["table_html"],
                        filenamehtml=session["filenamehtml"]
                    )

                else:
                    session["table_html"] = "No table found in the HTML file."
                    #return render_template('core/shortytable.html', table_html=None)
                    
                    return render_template(
                        'core/shortytable.html',
                        table_html=session["table_html"],
                        filenamehtml=session["filenamehtml"]
                    )
                                        
            except Exception as e:
                session["table_html"] = f"Error loading file: {e}"
                return render_template('core/shortytable.html', table_html=None)
        else:
            sf.get_ShortyTable()

    if "table_html" in session:
        return render_template(
            "core/shortytable.html",
            table_html = session["table_html"],
            filenamehtml = session.get("filenamehtml")
        )
    return render_template(
        'core/shortytable.html',
        table_html = None,
        filenamehtml = session.get("filenamehtml")
        )

@app.route("/shortyjson/", methods=['GET', 'POST'])
@app.route("/shortyjson/<table_json>")
@login_required
def shortyjson(table_json=None):
    if request.method == 'POST':
        filename = request.form.get('filename')
        if filename:
            # load from file
            path = '/Users/pg/proj/Shorty/-ShortyTables/' + filename
            try:
                with open(path, 'r') as f:
                    json_content = f.read()
                data = json.loads(json_content)
                # Convert JSON data to HTML table
                table_json = f'<table id="{filename}" class="ShortyTable">'
                if isinstance(data, list) and data:
                    # Assuming the JSON data is a list of dictionaries
                    headers = sorted(data[0].keys())
                    table_json += '<thead><tr>'
                    for header in headers:
                        table_json += f'<th><div>{header}</div></th>' 
                    table_json += '<th><div>Actions</div></th></tr></thead><tbody>'
                    for row in data:
                        table_json += '<tr>'
                        for cell in row.values():
                            table_json += f'<td><div>{cell.replace("\n", "<br>")}</div></td>'
                        table_json += '''
                            <td>
                                <button type="button" id="copy-button" class="smbtn smbtn-copy">Copy</button>
                                <button type="button" id="edit-button" class="smbtn smbtn-edit">Edit</button>
                                <button type="button" id="delete-button" class="smbtn smbtn-delete">Delete</button>
                            </td>
                        '''
                        table_json += '</tr>'
                    table_json += '</tbody></table>'
                    session["table_json"] = table_json
                    session["filenamejson"] = path
                    return render_template('core/shortyjson.html', table_json=session["table_json"])
                else:
                    session["table_json"] = "Invalid JSON format or empty data."
                    return render_template('core/shortyjson.html', table_json=None)
            except Exception as e:
                session["table_json"] = f"Error loading file: {e}"
                return render_template('core/shortyjson.html', table_json=None)
        else:
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

@app.route('/save_json', methods=['POST'])
@login_required
def save_json():
    data = request.get_json()
    json_data = data.get('json')
    path = data.get('path')
    if path:
        filename = path
        session['filenamejson'] = path
    else:
        filename = session.get('filenamejson', 'data.json')
    try:
        with open(filename, 'w') as file:
            json.dump(json_data, file, indent=4)
        # Update session with the new table HTML
        table_json = f'<table id="{os.path.basename(filename)}" class="ShortyTable">'
        if json_data:
            headers = sorted(json_data[0].keys())
            table_json += '<thead><tr>'
            for header in headers:
                table_json += f'<th><div>{header}</div></th>' 
            table_json += '<th><div>Actions</div></th></tr></thead><tbody>'
            for row in json_data:
                table_json += '<tr>'
                for cell in row.values():
                    table_json += f'<td><div>{cell.replace("\n", "<br>")}</div></td>'
                table_json += '''
                    <td>
                        <button type="button" id="copy-button" class="smbtn smbtn-copy">Copy</button>
                        <button type="button" id="edit-button" class="smbtn smbtn-edit">Edit</button>
                        <button type="button" id="delete-button" class="smbtn smbtn-delete">Delete</button>
                    </td>
                '''
                table_json += '</tr>'
            table_json += '</tbody></table>'
        else:
            table_json = "No data"
        session["table_json"] = table_json
        return jsonify({'message': 'File saved successfully', 'table_json': table_json})
    except Exception as e:
        return jsonify({'message': f'Error saving file: {e}'})

#

@app.route('/save_html', methods=['POST'])
@login_required
def save_html():
    
    data = request.get_json(silent=True)
    if not data:
        return jsonify({'message': 'Invalid HTML payload'}), 400
    
    html = data.get("html")
    path = data.get("path")

    if not html or not path:
        return jsonify({"error": "Missing html or path"}), 400
    
    html_content = data.get('html')
    path = data.get('path')

    if not html_content or not path:
        return jsonify({'message': 'Missing html or path'}), 400

    try:
        # Parse HTML
        soup = BeautifulSoup(html_content, 'html.parser')
        table = soup.find('table')

        if not table:
            return jsonify({'message': 'No table found'}), 400

        # Remove the runtime Actions column (if present) before persisting
        for row in table.find_all('tr'):
            cells = row.find_all('td')
            if len(cells) > 2:
                cells[-1].decompose()  # remove last cell

        # Strip style, id, and event attributes. Keep only the element classes
        # and a minimal set of attributes needed for editing/display (data-field,
        # contenteditable). This ensures the saved HTML is the barest structure
        # similar to HTML_Template.html.
        for tag in table.find_all(True):
            keep_attrs = {}
            if 'class' in tag.attrs:
                keep_attrs['class'] = tag.attrs.get('class')
            if tag.name == 'td' and 'contenteditable' in tag.attrs:
                keep_attrs['contenteditable'] = tag.attrs.get('contenteditable')
            if 'data-field' in tag.attrs:
                keep_attrs['data-field'] = tag.attrs.get('data-field')
            tag.attrs = keep_attrs

        # Write cleaned HTML back to file
        with open(path, 'w') as f:
            f.write(str(table))

        # For the response we want to include the runtime Actions column
        display_soup = BeautifulSoup(str(table), 'html.parser')
        for row in display_soup.find_all('tr'):
            # append the actions cell for the UI with proper classes for styling
            new_cell = display_soup.new_tag('td')
            copy_button = display_soup.new_tag('button', type='button', id='copy-button')
            copy_button.string = 'Copy'
            copy_button['class'] = 'smbtn smbtn-copy'
            new_cell.append(copy_button)
            edit_button = display_soup.new_tag('button', type='button', id='edit-button')
            edit_button.string = 'Edit'
            edit_button['class'] = 'smbtn smbtn-edit'
            new_cell.append(edit_button)
            delete_button = display_soup.new_tag('button', type='button', id='delete-button')
            delete_button.string = 'Delete'
            delete_button['class'] = 'smbtn smbtn-delete'
            new_cell.append(delete_button)
            row.append(new_cell)

        session["table_html"] = str(display_soup.find('table'))

        return jsonify({'message': 'HTML file saved successfully', 'table_html': session["table_html"]})

    except Exception as e:
        return jsonify({'message': f'Error saving HTML: {e}'})


@app.route('/create_table', methods=['POST'])
@login_required
def create_table():
    data = request.get_json(silent=True)
    filename = data.get('filename') if data else None
    if not filename:
        return jsonify({'error': 'Missing filename'}), 400
    # sanitize filename
    safe = re.sub(r'[^A-Za-z0-9_\- ]', '', filename).strip()
    if not safe:
        return jsonify({'error': 'Invalid filename'}), 400
    folder = '/Users/pg/proj/Shorty/-ShortyTables'
    path = os.path.join(folder, f"{safe}.html")
    if os.path.exists(path):
        return jsonify({'error': 'File already exists'}), 400
    try:
        # create a minimal two-column table with one editable row so the UI
        # displays at least one row when a new table is created
        initial_table = (
            f'<table id="{safe}" class="ShortyTable">'
            '<tbody>'
            '<tr>'
            '<td contenteditable="true"><div></div></td>'
            '<td contenteditable="true"><div></div></td>'
            '</tr>'
            '</tbody></table>'
        )
        with open(path, 'w') as f:
            f.write(initial_table)
        return jsonify({'success': True, 'filename': f'{safe}.html', 'path': path})
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/create_json', methods=['POST'])
@login_required
def create_json():
    data = request.get_json(silent=True)
    filename = data.get('filename') if data else None
    if not filename:
        return jsonify({'error': 'Missing filename'}), 400
    safe = re.sub(r'[^A-Za-z0-9_\- ]', '', filename).strip()
    if not safe:
        return jsonify({'error': 'Invalid filename'}), 400
    folder = '/Users/pg/proj/Shorty/-ShortyTables'
    path = os.path.join(folder, f"{safe}.json")
    if os.path.exists(path):
        return jsonify({'error': 'File already exists'}), 400
    try:
        # Create a new json file with a single empty row scaffold so
        # the UI displays a proper empty row when loading.
        scaffold = [{"long_note": "", "short_form": ""}]
        with open(path, 'w') as f:
            json.dump(scaffold, f, indent=4)
        return jsonify({'success': True, 'filename': f'{safe}.json', 'path': path})
    except Exception as e:
        return jsonify({'error': str(e)}), 500


#
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
