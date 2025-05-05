from flask import request
from bookish.models.book import Book
from bookish.models.author import Author
from bookish.models.copy import Copy
from bookish.app import db
from flask import Blueprint


book_controller = Blueprint("book_controller", __name__)


@book_controller.route("/healthcheck")
def health_check():
    return {"status": "OK"}


@book_controller.route("/book", methods=["POST", "GET"])
def get_all_books():
    if request.method == "POST":

        # Want to ask for information about book, then add to books, copies and possibly authors tables

        if request.is_json:
            data = request.get_json()

            # JSON should contain the following information:
            isbn = data.get("isbn")
            title = data.get("title")
            author_names = data.get("authors")
            quantity = data.get("quantity")

            # Check that the json is in the correct format
            if not all([isbn, title, author_names, quantity]):
                return {"error": "Missing required fields"}

            # Check if book with ISBN already exists in database
            if Book.query.get(isbn):
                return {"error": "Book with this ISBN already exists"}

            # Check if each author is already in database, if not then add them
            # Create a list of Author objects for this book (rather than just a list of their names as strings)
            author_objs = []
            for name in author_names:
                author = Author.query.filter_by(name=name).first()
                if not author:
                    author = Author(name=name)
                    db.session.add(author)
                author_objs.append(author)

            # Create the Book object and add it to the database
            new_book = Book(isbn=isbn, title=title, authors=author_objs)
            db.session.add(new_book)
            db.session.flush()  # This sends pending changes to the database without committing them
            # ie, don't want to add book yet because we need access to the copy ids

            # Add copies
            for _ in range(quantity):
                copy = Copy(isbn=isbn)
                db.session.add(copy)

            db.session.commit()
            return {"message": "New book has been created successfully."}
        else:
            return {"error": "The request payload is not in JSON format"}

    elif request.method == "GET":
        books = Book.query.all()
        results = [
            {
                "id": book.id,
                "title": book.Title,
                "author": book.Author,
                "isbn": book.ISBN,
                "quantity": book.Quantity,
            }
            for book in books
        ]
        return {"books": results}
    else:
        return {"error": "request method not supported"}
