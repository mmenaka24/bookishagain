from flask import request
from bookish.models import Author, Book, Copy, User
from bookish.app import db
from flask import Blueprint
from .utils import validate_isbn, validate_authors

# Create a utils.py file for reusable validation functions

book_controller = Blueprint("book_controller", __name__)


@book_controller.route("/healthcheck")
def health_check():
    return {"status": "OK"}


@book_controller.route("/newbook", methods=["POST"])
def add_book():

    # Ask for information about book, then add to books, copies and authors tables

    if request.is_json:
        data = request.get_json()

        # JSON should contain the following information:
        isbn = data.get("isbn")
        title = data.get("title")
        author_names = data.get("authors")
        quantity = data.get("quantity")

        # Check that the json has all the required fields
        if not all([isbn, title, author_names, quantity]):
            return {"error": "Missing required fields"}

        # Check types of variables are correct
        if not validate_isbn(isbn):
            return {"error": "ISBN must be a string of length 13"}
        if not isinstance(title, str):
            return {"error": "Book title must be a string"}
        if not validate_authors(author_names):
            return {"error": "Author names must be given as a list of strings"}
        if not isinstance(quantity, str):
            return {"error": "Quantity must be given as an integer (not a string!)"}

        # Check if book with ISBN already exists in database
        if Book.query.get(isbn):  # Use .get() to search by primary key
            return {"error": "Book with this ISBN already exists"}

        # Check if each author is already in database, if not then add them
        # Create a list of Author objects for this book (rather than just a list of their names as strings)
        author_objs = []
        for name in author_names:
            author = Author.query.filter_by(
                name=name
            ).first()  # Use .filter_by to search by something that isn't a primary key
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
        return {"message": f"New book {title} has been created successfully."}
    else:
        return {"error": "The request payload is not in JSON format"}


@book_controller.route("/book", methods=["GET"])
def get_books():

    # Want to give information about a specific book if the isbn is given, otherwise show all books
    isbn = request.args.get("isbn")  # request params are strings

    if isbn:
        book = Book.query.get(isbn)

        if not book:
            return {"error": "No book with that ISBN found"}

        number_of_copies = len(book.copies)
        available_copies = 0
        copy_info = []
        for copy in book.copies:
            if copy.is_checked_out:
                user_id = copy.user_id
                user = User.query.get(user_id)
                copy_info.append(
                    f"Copy {copy.copy_id} is checked out by user {user.username}"
                )
            else:
                available_copies += 1
                copy_info.append(f"Copy {copy.copy_id} is available")

        results = [
            {
                "total number of copies": number_of_copies,
                "available copies": available_copies,
                "copy info": copy_info,
            }
        ]

        return {f"{book.title}": results}

    else:
        books = Book.query.order_by(
            Book.title
        ).all()  # Orders books alphabetically by title

        results = [
            {
                "isbn": book.isbn,
                "title": book.title,
                "authors": [author.name for author in book.authors],
                "number_of_copies": len(book.copies),
            }
            for book in books
        ]

        return {"books": results}


@book_controller.route("/newuser", methods=["POST"])
def add_user():

    if request.is_json:
        data = request.get_json()

        username = data.get("username")

        if not username:
            return {"error": "JSON must contain username field"}

        if not isinstance(username, str):
            return {"error": "Username must be a string"}

        if User.query.filter_by(username=username).first():
            return {"error": "This username has already been taken"}

        new_user = User(username=username)
        db.session.add(new_user)

        db.session.commit()
        user_id = User.query.filter_by(username=username).first().user_id
        return {
            "message": f"New user {username} has been added - your user id is {user_id}"
        }

    else:
        return {"error": "The request payload is not in JSON format"}


@book_controller.route("/user", methods=["GET"])
def see_users_books():

    user_id = request.args.get("user_id")
    username = request.args.get("username")
    user = None

    if user_id:
        user = User.query.get(user_id)
        if not user:
            return {"error": "No user with that user id found"}
    else:
        if username:
            user = User.query.filter_by(username=username).first()
            if not user:
                return {"error": "No user with that username found"}
        else:
            return {"error": "Please enter query parameters for user_id or username"}

    user_copies = user.checked_out_copies
    if not user_copies:
        return {"message": f"User {user.username} has no books checked out currently"}

    else:
        results = [
            {
                "title": copy.book.title,
                "authors": [author.name for author in copy.book.authors],
            }
            for copy in user_copies
        ]

        return {f"checked out copies for user {user.username}": results}


@book_controller.route("/addcopies", methods=["POST"])
def add_copies():

    if request.is_json:

        data = request.get_json()

        isbn = data.get("isbn")
        quantity_to_add = data.get("quantity")

        if not all([isbn, quantity_to_add]):
            return {"error": "Missing required fields"}

        if not validate_isbn(isbn):
            return {"error": "ISBN must be a string of length 13"}
        if not isinstance(quantity_to_add, int):
            return {"error": "Quantity must be an integer"}

        # Check that there is already a book with this isbn
        book = Book.query.get(isbn)
        if not book:
            return {"error": "Book with this ISBN not found"}

        for _ in range(quantity_to_add):
            copy = Copy(isbn=isbn)
            db.session.add(copy)

        db.session.commit()

        return {
            "message": f"Successfully added {quantity_to_add} copies of {book.title}"
        }

    else:
        return {"error": "The request payload is not in JSON format"}


@book_controller.route("/checkout", methods=["PUT"])
def checkout_copy():

    if request.is_json:

        data = request.get_json()

        user_id = data.get("user_id")
        if not user_id:
            username = data.get("username")
            if username:
                user = User.query.filter_by(username=username).first()
                if user:
                    user_id = user.user_id
                else:
                    return {"error": "No user with that username found"}
        else:
            user = User.query.get(user_id)
            if not user:
                return {"error": "No user with that ID found"}

        copy_id = data.get("copy_id")
        if not all([user_id, copy_id]):
            return {"error": "Missing required fields"}

        copy = Copy.query.get(copy_id)
        if not copy:
            return {"error": "No copy with that ID found"}
        if copy.is_checked_out:
            return {"error": "This copy is already checked out"}

        # Update copy table
        copy.user_id = user_id
        copy.is_checked_out = True

        db.session.commit()

        return {
            "message": f"Successfully checked out {copy.book.title} for user {copy.user.username}"
        }
    else:
        return {"error": "The request payload is not in JSON format"}


@book_controller.route("/return", methods=["PUT"])
def return_book():

    if request.is_json:

        data = request.get_json()

        copy_id = data.get("copy_id")
        if not copy_id:
            return {"error": "Missing required fields"}

        # Update copy table
        copy = Copy.query.get(copy_id)
        if not copy:
            return {"error": "No copy with that ID found"}
        if not copy.is_checked_out:
            return {"error": "This copy was already returned"}
        prev_user = copy.user.username

        # Update copy table
        copy.user_id = None
        copy.is_checked_out = False

        db.session.commit()

        return {
            "message": f"Successfully returned {copy.book.title} for user {prev_user}"
        }
    else:
        return {"error": "The request payload is not in JSON format"}


@book_controller.route("/search", methods=["GET"])
def search_books():

    author_name = request.args.get("author")
    title = request.args.get("title")

    if not (author_name or title):
        return {"error": "Please enter query parameters for author and/or title"}
    # Don't need to check types here - if a query param is of the wrong type it will just return no books matching search

    # Build up query
    query = Book.query

    if author_name:
        author = Author.query.filter_by(name=author_name).first()
        if not author:
            return {"message": "No books matching your search have been found"}
        query = query.filter(Book.authors.contains(author))

    if title:
        query = query.filter_by(title=title)

    books = query.all()

    if not books:
        return {"message": "No books matching your search have been found"}
    else:
        results = [
            {
                "isbn": book.isbn,
                "title": book.title,
                "authors": [author.name for author in book.authors],
                "number_of_copies": len(book.copies),
            }
            for book in books
        ]
        return {"books": results}
