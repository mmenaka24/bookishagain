from flask import Flask
import os
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate


db = SQLAlchemy()


def create_app():
    app = Flask(__name__)

    app.config.from_object(os.environ["APP_SETTINGS"])

    app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

    db.init_app(app)
    Migrate(app, db)

    from bookish.controllers.BookController import book_controller

    app.register_blueprint(book_controller)

    with app.app_context():
        from bookish.models.author import Author
        from bookish.models.book import Book
        from bookish.models.copy import Copy
        from bookish.models.junction_tables import BookAuthor
        from bookish.models.user import User

        db.create_all()

    return app
