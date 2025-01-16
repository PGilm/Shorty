# Entry point for the application.
from . import app    # For application discovery by the 'flask' command.
# from . import views  # For import side-effects of setting up routes.

# Windows use $env:FLASK_APP=webapp if you're using PowerShell, or set FLASK_APP=webapp if you're using Command Prompt.

# Navigate into the hello_app folder, then launch the program using python -m flask run