from bookish.app import db
from .book import Book


class Copy(db.Model):
    __tablename__ = "Copies"

    copy_id = db.Column(db.Integer, primary_key=True)

    isbn = db.Column(db.String(13), db.ForeignKey("Books.isbn"), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey("Users.user_id"), nullable=True)
    # These lines create the foreign key constraints, but don't automatically give access to the Book/User objects

    is_checked_out = db.Column(db.Boolean, nullable=False)

    book = db.relationship("Book", back_populates="copies")
    user = db.relationship("User", back_populates="checked_out_copies")
    # Tells SQLAlchemy to give access to the Book/User object associated with each Copy and let each Book/User access its Copies

    def __init__(self, isbn):
        book = Book.query.filter_by(isbn=isbn).first()
        if not book:
            raise ValueError(f"Book with ISBN {isbn} not found")
        self.isbn = isbn
        self.is_checked_out = False
        self.book = book

    def __repr__(self):
        return f"<Copy: id={self.copy_id}, isbn={self.isbn}, book={self.book.title}, is_checked_out={self.is_checked_out}>"

    def serialize(self):
        return {
            "id": self.copy_id,
            "isbn": self.isbn,
            "is_checked_out": self.is_checked_out,
        }
