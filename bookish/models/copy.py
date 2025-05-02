from bookish.app import db
from .book import Book


class Copy(db.Model):
    __tablename__ = "Copies"

    id = db.Column(db.Integer, primary_key=True)
    isbn = db.Column(
        db.String(13), db.ForeignKey("Books.isbn"), nullable=False
    )  # This line creates the foreign key constraint, but doesn't automatically give access to the Book object
    is_checked_out = db.Column(db.Boolean, nullable=False)

    book = db.relationship(
        "Book", backref="copies"
    )  # Tells SQLAlchemy to give access to the Book object associated with each Copy and let each Book access its Copies

    def __init__(self, isbn):
        self.isbn = isbn
        self.is_checked_out = False

        # Automatically fetch the associated Book from the database
        self.book = Book.query.filter_by(isbn=isbn).first()

    def __repr__(self):
        return f"<Copy: id={self.id}, isbn={self.isbn}, book={self.book.title}, is_checked_out={self.is_checked_out}>"

    def serialize(self):
        return {
            "id": self.id,
            "isbn": self.isbn,
            "is_checked_out": self.is_checked_out,
        }
