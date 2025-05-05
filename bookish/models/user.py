from bookish.app import db


class User(db.Model):
    __tablename__ = "Users"

    user_id = db.Column(db.Integer, primary_key=True)
    username = db.Column(
        db.String(), nullable=False
    )  # Will enforce that username is unique by not adding new users with same username (rather than setting it as a primary key)

    # one-to-many relationship with copies
    checked_out_copies = db.relationship("Copy", back_populates="user", lazy=True)

    def __init__(self, username):
        self.username = username
        # By removing id from __init__, SQLAlchemy automatically gives a unique integer id
        # By default, an integer primary key column will be auto-incremented, so don't need to manually assign a value

    def __repr__(self):
        return f"<User: id={self.user_id}, username={self.username}>"

    def serialize(self):
        return {
            "id": self.user_id,
            "username": self.username,
            "checked_out_copies": [copy.copy_id for copy in self.checked_out_copies],
        }
