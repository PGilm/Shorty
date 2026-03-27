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

- `APP_SETTINGS` (usually `config.DevelopmentConfig`)
- `SECRET_KEY`
- `DATABASE_URL`
- `APP_NAME`

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

- `ShortyHTML` to edit snippet rows stored in `-ShortyTables/<username>/*.html`
- `ShortyJSON` to edit snippet rows stored in `-ShortyTables/<username>/*.json`

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
