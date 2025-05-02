from bookish.app import db


class User(db.Model):
    __tablename__ = "Users"

    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(), nullable=False)

    # one-to-many relationship with copies
    checked_out_copies = db.relationship("Copy", backref="Users", lazy=True)

    def __init__(self, username):
        self.username = username
        # By removing id from __init__, SQLAlchemy automatically gives a unique integer id
        # By default, an integer primary key column will be auto-incremented, so don't need to manually assign a value

    def __repr__(self):
        return f"<User: id={self.id}, username={self.username}>"

    def serialize(self):
        return {
            "id": self.id,
            "username": self.username,
            "checked_out_copies": [copy.id for copy in self.checked_out_copies],
        }
