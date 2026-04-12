# Shorty

Shorty is a Flask application for storing and editing reusable text snippets in table form.
It supports two datatable types:

- `ShortyHTML`: snippet rows stored as HTML tables.
- `ShortyJSON`: snippet rows stored as JSON objects.

## Requirements

- Python 3.11+ (recommended)
- `pip`
- Virtual environment tooling (`python3 -m venv`)

## Setup

1. Create and activate a virtual environment:

   ```bash
   python3 -m venv .venv
   source .venv/bin/activate
   ```

2. Install dependencies:

   ```bash
   pip install -r requirements.txt
   ```

3. Create your environment file:

   ```bash
   cp .env.example .env
   ```

4. Update `.env` as needed:

- `APP_SETTINGS`: choose `config.DevelopmentConfig` for local work, `config.TestingConfig` for tests, and `config.ProductionConfig` for deployed environments.
- `SECRET_KEY`: always replace with a long random value outside local-only development.
- `DATABASE_URL`: keep `sqlite:///db.sqlite` for single-user local usage; switch to Postgres (for example `postgresql://...`) for shared or production use.
- `APP_NAME`: display/issuer label used in parts of the UI and 2FA metadata; change for rebranding.
- `SHORTY_ADMIN_USERS`: comma-separated usernames that should have access to the admin page (`/admin`).
- `SHORTY_DEFAULT_STORAGE_ROOT`: optional absolute folder for default per-user storage. If omitted, Shorty uses project-local `-ShortyTables/<username>/`.
- `FORCE_SECURE_COOKIES`: set to `1` only when traffic is HTTPS end-to-end; keep `0` for plain local HTTP.
- `ENABLE_PROXYFIX`: keep `1` when behind nginx/ALB/reverse proxy so Flask reads forwarded host/scheme correctly; set `0` for direct local runs.
- `FLASK_RUN_HOST` / `FLASK_RUN_PORT`: change when the app must bind to a different interface or port.
- `FLASK_DEBUG`: keep `1` only for local debugging.

## Database Migration Commands

Run these the first time:

```bash
./.venv/bin/python manage.py db init
./.venv/bin/python manage.py db migrate
./.venv/bin/python manage.py db upgrade
```

For future schema changes:

```bash
./.venv/bin/python manage.py db migrate
./.venv/bin/python manage.py db upgrade
```

## Run the App

Development server:

```bash
./.venv/bin/python manage.py run --host 0.0.0.0 --port 5004
```

Production-style command example:

```bash
gunicorn -b 0.0.0.0:5004 -w 4 -k gevent 'manage:app'
```

## How the Snippet UI Works

After login, use the left navigation:

- `ShortyHTML` to edit snippet rows stored in `-ShortyTables/<username>/*.html` (default)
- `ShortyJSON` to edit snippet rows stored in `-ShortyTables/<username>/*.json` (default)

User-selected storage roots (USB/cloud-synced folders) follow the same layout:

- `<selected-root>/*.html`
- `<selected-root>/*.json`

Browser-first mode for remote users:

- In `ShortyHTML` or `ShortyJSON`, click `Connect Local Folder` to use the browser File System Access API.
- After permission is granted, create/load/save actions run against the user's own local folder rather than the server filesystem.

Top-row controls on each snippet page:

- `New ShortyHTML` / `New ShortyJSON`: creates a new file.
- `Add Row`: inserts a new editable row at the top.
- `Reorder Rows`: turns on drag-and-drop row ordering.
- `Done Reordering`: turns off drag mode and saves the new order.
- `Double Row Height` / `Normal Row Height`: toggles row content area height.

Per-row controls:

- `Copy`: copies snippet text from the cell left of the action buttons.
- `Edit` / `Save`: toggles row editing and persists all table changes.
- `Delete`: removes a row and persists the updated table.

## Notes

- Session and login state are required for most snippet routes.
- The app uses Flask-Login plus optional 2FA flow in `accounts` routes.
- You can inspect all routes with:

  ```bash
  ./.venv/bin/python manage.py routes
  ```
