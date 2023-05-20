from tinydb import TinyDB

db = TinyDB("db.json", indent=2, encoding="utf-8", ensure_ascii=False)


def get_db():
    return db
