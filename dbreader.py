from api import Database

db = Database()
db.create()
for value in db.getAll('users'):
    print(value)
