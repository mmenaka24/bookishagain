from bookish.app import db


class BookAuthor(db.Model):
    __tablename__ = "book_author"

    book_isbn = db.Column(db.String(13), db.ForeignKey("Books.isbn"), primary_key=True)
    author_id = db.Column(db.Integer, db.ForeignKey("Authors.id", primary_key=True))
