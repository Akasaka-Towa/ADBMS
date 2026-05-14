from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager


db = SQLAlchemy()
login_manager = LoginManager()
login_manager.login_view = "auth.login"

from .user import User  # noqa: E402
from .file import StoredFile, FileVersion, FileShare  # noqa: E402
