from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate

from .book import Book
from .author import Author
from .copy import Copy
from .user import User
from .junction_tables import BookAuthor

db = SQLAlchemy()
migrate = Migrate(db)

__all__ = ["Book", "Author", "Copy", "User"]
