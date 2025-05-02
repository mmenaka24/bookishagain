from bookish.app import db


class Author(db.Model):
    __tablename__ = "Authors"

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(), nullable=False)

    # many-to-many relationship with books through the book_author junction table
    books = db.relationship("Book", secondary="book_author", back_populates="authors")

    def __init__(self, name):
        self.name = name

    def __repr__(self):
        return "<Author: id={self.id}, name={self.name}>"

    def serialize(self):
        return {
            "id": self.id,
            "name": self.name,
            "books": [book.isbn for book in self.books],
        }
