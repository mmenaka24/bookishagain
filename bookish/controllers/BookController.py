from flask import request
from bookish.models.book import Book
from bookish.app import db
from flask import Blueprint


book_controller = Blueprint("book_controller", __name__)


@book_controller.route("/healthcheck")
def health_check():
    return {"status": "OK"}


@book_controller.route("/book", methods=["POST", "GET"])
def get_all_books():
    if request.method == "POST":
        if request.is_json:
            data = request.get_json()
            new_example = Book(
                Title=data["title"],
                Author=data["author"],
                ISBN=data["isbn"],
                Quantity=data["quantity"],
            )
            db.session.add(new_example)
            db.session.commit()
            return {"message": "New example has been created successfully."}
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
