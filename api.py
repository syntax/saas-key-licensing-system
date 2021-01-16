import os
import sqlite3


class Database():
    def __init__(self):
        self.conn = sqlite3.connect('./licenses.db')
        self.c = self.conn.cursor()

    def create(self):
        if os.path.getsize('licenses.db') != 0:
            return 'DB File already exists and has already been created.'
        else:
            self.c.execute('CREATE TABLE users (username text PRIMARY KEY, fName text, sName text, emailAddress text, password text)')
            self.c.execute('CREATE TABLE licenses (license text PRIMARY KEY, username text, boundToUser boolean, boundToDevice boolean, HWID string, devicename string)')
            self.conn.commit()
            return 'Created DB file'

    def removeTable(self):
        self.c.execute('DROP TABLE licenses')
        self.conn.commit()

    def addToUsers(self,values):
        self.c.execute(f'''INSERT INTO users(username,fName,sName,emailAddress,password))
              VALUES(?, ?, ?, ?, ?)''', tuple(values.split(',')))
        self.conn.commit()

    def searchUsers(self, email,user):
        self.c.execute(f'''SELECT username, emailAddress FROM users WHERE emailAddress = ? OR username = ?''', (email,user) )
        result = self.c.fetchone()
        return result

    def hwidAndDeviceToTable(self,license,hwid,devname,activestatus): #database functions that the api call might need to make
        print(license,hwid,devname)
        self.c.execute(f'''UPDATE licenses
                SET HWID = '{hwid}', devicename = '{devname}', boundToDevice = '{activestatus}'
                WHERE license    = '{license}';''')
        self.conn.commit()

    def activatedToTable(self,license,activated: bool):
        self.c.execute(f'''UPDATE licenses
                        SET activated = {activated}
                        WHERE license = {license};''')
        self.conn.commit()

    def getFromTable(self,license):
        self.c.execute(f'''SELECT *
                        FROM licenses
                        WHERE license = ?;''', (license,))
        return self.c.fetchall()

    def removeFromTable(self,license):
        self.c.execute(f'''DELETE FROM licenses 
                        WHERE license = {license};''')
        self.conn.commit()

    def closeConnection(self):
        self.conn.close()


#this is not really needed, only for testing.
# db = Database()
# db.create()
# #testing adding fields to database
# db.addToTable_wholerow('sam,barnett,sambarnettbusiness@gmail.com,killthecats!!,12345678,active,91294macbook,Sams macbook')
# db.addToTable_wholerow('ollie,blair,ollieblair.03@gmail.com,Icat112!!,1292-9412-1539,active,windowsanddat, Ollies XPS')
#
# licenses = [{'id': 1,'key':'asbd918b2819basd89'}, {'id': 2,'key':'iniboniogb123bobo'}]



# def genlicensesession():  # will need to justify why this is ALWAYS random and crytographically secure
#     return hexlify(os.urandom(16))


#
#
# if __name__ == '__main__':
#     db.create()
#     app.run()
