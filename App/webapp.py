# Entry point for the application.
from . import app    # Set in __init__.py for application base dir discovery by the 'flask' command.
from .core import views  # For import side-effects of setting up routes.
