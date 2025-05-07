from bookish.app import db
from bookish.models import Author, Copy, User


def validate_isbn(isbn):
    if not (isinstance(isbn, str) and len(isbn) == 13):
        return False
    return True


def validate_authors(authors):
    if not isinstance(authors, list):
        return False
    if not all(isinstance(name, str) for name in authors):
        return False
    return True


def get_or_create_author(name):
    author = Author.query.filter_by(name=name).first()
    if not author:
        author = Author(name=name)
        db.session.add(author)
    return author


def create_copies(isbn, quantity):
    for _ in range(quantity):
        db.session.add(Copy(isbn - isbn))


def find_user(user_id=None, username=None):
    user = None
    if user_id:
        if isinstance(user_id, int):
            user = User.query.get(user_id)
            if not user:
                return None
        else:
            return None
    elif username:
        user = User.query.filter_by(username=username).first()
        if not user:
            return None
    else:
        return None
    return user
