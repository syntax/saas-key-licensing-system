from flask import Flask, jsonify, abort, make_response, request
import os
from binascii import hexlify
import sqlite3


class Database():
    def __init__(self):
        self.conn = sqlite3.connect('./main.db')
        self.c = self.conn.cursor()

    def create(self):
        if os.path.getsize('main.db') != 0:
            return 'DB File already exists and has already been created.'
        else:
            self.c.execute('CREATE TABLE licenses (fName text, sName text, emailAddress text, password text, license text, active boolean, HWID string)')
            self.conn.commit()
            return 'Created DB file'

    def removeTable(self):
        self.c.execute('DROP TABLE licenses')
        self.conn.commit()

    def addToTable_wholerow(self):
        self.c.execute('''INSERT INTO licenses(fName,sName,emailAddress,password,license,active,HWID)
              VALUES(?,?,?)''')
        self.conn.commit()
        pass

    def editTable_specificcol(self):
        pass

    def getFromTable(self):
        pass

    def removeFromTable(self):
        pass


db = Database()

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
    license = [license for license in licenses if license['id'] == licenseid]
    if len(license) == 0:
        abort(404)
    return jsonify({'license': license[0]})


@app.route('/api/v1/licenses', methods=['POST'])
def create_license():
    if not request.json or not 'key' in request.json:
        abort(400)
    license = {'id': licenses[-1]['id'] + 1,'key':request.json['key'] }
    licenses.append(license)
    print(licenses)
    return jsonify({'license': license}), 201


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
