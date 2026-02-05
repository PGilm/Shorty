#!/usr/bin/env python3
"""
Generate "Shorty Users" datatables (HTML and JSON) into -ShortyTables/PGilm.
Run this from the project root in the same environment as the Flask app.
"""
import os
import json
import sys
import traceback

# Adjust this path if your app uses a different base
BASE = '/Users/pg/proj/Shorty/-ShortyTables/PGilm'

# Make project root importable so `from App import ...` works when run as a script
PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)

os.makedirs(BASE, exist_ok=True)

def generate_shorty_users(base_dir=BASE):
    """Generate Shorty Users JSON and HTML files into base_dir.
    Returns tuple (json_path, html_path).
    """
    try:
        from App import app, db
        from App.accounts.models import User
    except Exception as e:
        raise

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


if __name__ == '__main__':
    try:
        j, h = generate_shorty_users()
        print('Wrote', j)
        print('Wrote', h)
        print('Done.')
    except Exception as e:
        print('Could not import app or models:', e)
        traceback.print_exc()
        sys.exit(1)
