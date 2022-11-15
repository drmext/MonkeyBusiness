from tinydb import TinyDB

db = TinyDB("db.json", indent=4)


def get_db():
    return db
