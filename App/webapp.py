# Entry point for the application.
from . import app    # For application discovery by the 'flask' command.
# from . import views  # For import side-effects of setting up routes.

# TO RUN ANYWHERE
# Windows: Powershell:  $env:FLASK_APP=webapp
# Windows: Command:     set FLASK_APP=webapp

# Navigate to "app" folder, then run: python -m flask run