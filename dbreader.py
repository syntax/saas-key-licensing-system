from api import Database

db = Database()
db.create()
print(db.getAll())