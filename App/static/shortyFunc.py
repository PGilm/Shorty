import platform

import App.core.views as a

import pyotp
import qrcode

def generate_2fa_secret():
    return pyotp.random_base32()

def generate_qr_code(secret, username):
    otp_uri = pyotp.totp.TOTP(secret).provisioning_uri(name=username, issuer_name="YourAppName")
    img = qrcode.make(otp_uri)
    img.save(f"{username}_qrcode.png")

# db = SQLAlchemy()
class User(UserMixin, db.Model):
    id = a.db.Column(a.db.Integer, primary_key=True)
    username = a.db.Column(a.db.String(150), unique=True, nullable=False)
    password = a.db.Column(a.db.String(150), nullable=False)
    two_factor_secret = a.db.Column(a.db.String(16))

def get_ShortyJson() -> str:
    file = a.request.files.get('file')
    if file and file.filename:
        try:
            json_content = file.read()
            data = a.json.loads(json_content)
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
            
            while "table_json" in a.session:
                a.session.pop("table_json", None)
            a.session["table_json"] = str(table_json)
            a.session["filenamejson"] = file.filename
            return a.render_template('core/shortyjson.html', table_json=a.session["table_json"])
        except Exception as e:
            a.session["table_json"] = f"Error processing JSON file: {e}"
    return a.session["table_json"]

def get_ShortyTable() -> str:
    file = a.request.files.get('file')
    if file and file.filename:
        try:
            html_content = file.read()
            soup = a.BeautifulSoup(html_content, 'html.parser')
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
                while "table_html" in a.session:
                    a.session.pop("table_html", None)
                a.session["table_html"] = str(table)
                a.session["filenamehtml"] = file.filename
                return a.render_template('core/shortytable.html', table_html=a.session["table_html"])
            else:
                a.session["table_html"] = "No table found in the HTML file."
        except Exception as e:
            a.session["table_html"] = f"Error processing file: {e}"
    return a.session["table_html"]

def get_port():
    if 'Microsoft' in platform.uname().release:  # "Linux" under WSL
        if platform.node() == "SBK": return 5002
        if platform.node() == "SAG": return 5004
    elif platform.system() == "Windows":  # running under "Windows"
        if platform.node() == "SBK": return 5001
        if platform.node() == "SAG": return 5003
    return 5001  # default port

if __name__ == "__main__":
    print(get_port())
