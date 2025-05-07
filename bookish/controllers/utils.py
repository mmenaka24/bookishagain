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