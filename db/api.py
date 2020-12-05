from flask import Flask, jsonify, abort, make_response, request
import os
from binascii import hexlify
import sqlite3


class Database():
    def __init__(self):
        self.conn = sqlite3.connect('./licenses.db')
        self.c = self.conn.cursor()

    def create(self):
        if os.path.getsize('licenses.db') != 0:
            return 'DB File already exists and has already been created.'
        else:
            self.c.execute('CREATE TABLE licenses (fName text, sName text, emailAddress text, password text, license text, active boolean, HWID string)')
            self.conn.commit()
            return 'Created DB file'

    def removeTable(self):
        self.c.execute('DROP TABLE licenses')
        self.conn.commit()

    def addToTable_wholerow(self,values):
        self.c.execute(f'''INSERT INTO licenses(fName,sName,emailAddress,password,license,active,HWID)
              VALUES(?, ?, ?, ?, ?, ?, ?)''', tuple(values.split(',')))
        self.conn.commit()

    def hwidAndDeviceToTable(self,license,hwid,devname): #database functions that the api call might need to make
        self.c.execute(f'''UPDATE licenses
                SET hwid = {hwid}, devicename = {devname}
                WHERE licensekeyID = {license};''')
        self.conn.commit()

    def activatedToTable(self,license,activated: bool):
        self.c.execute(f'''UPDATE licenses
                        SET activated = {activated}
                        WHERE licensekeyID = {license};''')
        self.conn.commit()

    def getFromTable(self,license):
        self.c.execute(f'''SELECT *
                        FROM licenses
                        WHERE license = ?;''', (license,))
        return self.c.fetchall()

    def removeFromTable(self):
        pass

    def closeConnection(self):
        self.conn.close()


db = Database()
#testing adding fields to database
db.addToTable_wholerow('sam,barnett,sambarnettbusiness@gmail.com,killthecats!!,12345678,active,91294macbook')
db.addToTable_wholerow('ollie,blair,ollieblair.03@gmail.com,Icat112!!,1292-9412-1539,active,windowsanddat')

app = Flask(__name__)

licenses = [{'id': 1,'key':'asbd918b2819basd89'}, {'id': 2,'key':'iniboniogb123bobo'}]



# def genlicensesession():  # will need to justify why this is ALWAYS random and crytographically secure
#     return hexlify(os.urandom(16))


@app.errorhandler(404)
def not_found():
    return make_response(jsonify({'error': 'not found'}), 404)


@app.route('/api/v1/licenses', methods=['GET'])
def get_licenses():
    return jsonify({'licenses': licenses})


@app.route('/api/v1/licenses/<int:licenseid>', methods=['GET'])
def get_specific_license(licenseid):
    dbtemp = Database()
    license = dbtemp.getFromTable(licenseid)
    if len(license) == 0:
        abort(404)
    else:
        license = license[0] #testing purposes only
        license_dict = {
                        "first_name": license[0],
                        "last_name": license[1],
                        "email": license[2],
                        "pw": license[3],
                        "license_key": license[4],
                        "active_status": license[5],
                        "hwid_identifier": license[6]
                        }
    dbtemp.closeConnection()
    return jsonify({'license': license_dict})


@app.route('/api/v1/licenses', methods=['POST'])
def create_license():
    if not request.json or not {'first_name', 'last_name', 'email', 'pw', 'license_key','active_status','hwid_identifier'}.issubset(set(request.json)):
        abort(400) #either not all params provided, or not posted correctly
    else:
        formattedjson = ','.join(list(request.json.values()))
        dbtemp = Database()
        try:
            dbtemp.addToTable_wholerow(formattedjson)
            dbtemp.closeConnection()
            return jsonify({'license': request.json}), 201
        except Exception as e: #closes connection incase of issue writing to db, as to not present later issues
            print(e)
            dbtemp.closeConnection()
            abort(500)


@app.route('/api/v1/licenses<int:licenseid>', methods=['DELETE'])
def delete_task(licenseid):
    license = [license for license in licenses if license['id'] == licenseid]
    if len(license) == 0:
        abort(404)
    licenses.remove(license[0])
    return jsonify({'result': True})


if __name__ == '__main__':
    db.create()
    app.run()
