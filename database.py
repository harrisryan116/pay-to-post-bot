import shelve

DB_NAME = "credits.db"

def add_credit(user_id: int):
    with shelve.open(DB_NAME) as db:
        db[str(user_id)] = db.get(str(user_id), 0) + 1

def has_credit(user_id: int) -> bool:
    with shelve.open(DB_NAME) as db:
        return db.get(str(user_id), 0) > 0

def use_credit(user_id: int):
    with shelve.open(DB_NAME) as db:
        current = db.get(str(user_id), 0)
        if current > 0:
            db[str(user_id)] = current - 1
