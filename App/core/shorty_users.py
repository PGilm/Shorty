import os
import json
from App import app

BASE_DEFAULT = '/Users/pg/proj/Shorty/-ShortyTables/PGilm'

def generate_shorty_users(base_dir: str = None):
    """Generate Shorty Users JSON and HTML files into base_dir.
    This function must be called within an application context or will
    create one internally when used from request handlers.
    """
    if base_dir is None:
        base_dir = BASE_DEFAULT

    from App.accounts.models import User
    os.makedirs(base_dir, exist_ok=True)
    with app.app_context():
        users = User.query.all()
        data = []
        for u in users:
            data.append({'username': u.username, 'email': getattr(u, 'emailaddress', '')})

        # Write JSON
        json_path = os.path.join(base_dir, 'Shorty Users.json')
        with open(json_path, 'w') as jf:
            json.dump(data, jf, indent=2)

        # Write HTML table
        html_path = os.path.join(base_dir, 'Shorty Users.html')
        with open(html_path, 'w') as hf:
            hf.write('<table id="Shorty Users" class="ShortyTable">\n')
            hf.write('<thead><tr><th><div>username</div></th><th><div>email</div></th><th><div>Actions</div></th></tr></thead>\n')
            hf.write('<tbody>\n')
            for row in data:
                hf.write('<tr>')
                hf.write(f"<td><div>{row['username']}</div></td>")
                hf.write(f"<td><div>{row['email']}</div></td>")
                hf.write('<td><button type="button" class="smbtn smbtn-copy">Copy</button>')
                hf.write('<button type="button" class="smbtn smbtn-edit">Edit</button>')
                hf.write('<button type="button" class="smbtn smbtn-delete">Delete</button></td>')
                hf.write('</tr>\n')
            hf.write('</tbody></table>\n')

    return json_path, html_path
