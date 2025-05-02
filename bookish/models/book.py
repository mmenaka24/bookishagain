from bookish.app import db


class Book(db.Model):
    # This sets the name of the table in the database
    __tablename__ = "Books"

    # Here we outline what columns we want in our database
    isbn = db.Column(db.String(13), primary_key=True)  # Using ISBN as the primary key
    title = db.Column(db.String(), nullable=False)

    # many-to-many relationship with authors through the book_author table
    authors = db.relationship("Author", secondary="book_author", back_populates="books")

    # one-to-many relationship with copies
    copies = db.relationship("Copy", backref="Books", lazy=True)
    # lazy = True means that the related copies will not be loaded from the database until they are explicitly needed
    # ie, the query to fetch them will be issued only when needed

    def __init__(self, isbn, title, authors):
        self.isbn = isbn
        self.title = title
        if not authors:
            raise ValueError("All books must have at least one author")
        self.authors = authors

    def __repr__(self):
        return f"<Book(isbn={self.isbn}, title={self.title})>"

    def serialize(self):
        return {
            "isbn": self.isbn,
            "title": self.title,
            "authors": [author.name for author in self.authors],
            "copies": [copy.id for copy in self.copies],
        }
