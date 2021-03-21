from api import Database

db = Database()
db.create()
for value in db.getAll('licenses'):
    print(value)
