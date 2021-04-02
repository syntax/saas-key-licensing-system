import os
import sqlite3
from datetime import datetime


class Database():
    def __init__(self):
        self.conn = sqlite3.connect('./licenses.db')
        self.c = self.conn.cursor()

    def create(self):
        if os.path.getsize('licenses.db') != 0:
            return 'DB File already exists and has already been created.'
        else:
            self.c.execute('CREATE TABLE users (username text PRIMARY KEY, fName text, sName text, emailAddress text, password text, admin bool)')
            self.c.execute('CREATE TABLE licenses (license text PRIMARY KEY, username text, boundToUser boolean, boundToDevice boolean, HWID string, devicename string, nextrenewal string, plan string, stripeSessionID string)')
            self.c.execute('CREATE TABLE plans (name text PRIMARY KEY, interval integer, amount float)')
            self.conn.commit()
            return 'Created DB file'

    def closeConnection(self):
        self.conn.close()
        return

    # non specific functions

    def getCountofTable(self, table):
        self.c.execute(f'''SELECT COUNT(*) FROM {table}''')
        result = self.c.fetchone()
        return result[0]

    def getConditionalCountofTable(self, table, column, condition):
        self.c.execute(f'''SELECT COUNT(*) FROM {table} WHERE {column} = {condition}''')
        result = self.c.fetchone()
        return result[0]

    def getMostPopular(self,table, column):
        self.c.execute(f'''SELECT {column}, COUNT({column}) AS value_occurance FROM {table} GROUP BY {column} ORDER BY value_occurance DESC LIMIT 1;''')
        result = self.c.fetchone()
        return result

    # user related functions

    def getAll(self, dbname):
        self.c.execute(f'''SELECT * FROM {dbname}''')
        result = self.c.fetchall()
        return result

    def removeTable(self):
        self.c.execute('DROP TABLE licenses')
        self.conn.commit()
        return

    def searchUsersByUsername(self, user):
        self.c.execute(f'''SELECT * FROM users WHERE username = ?''', (user,))
        result = self.c.fetchone()
        return result

    def addToUsers(self, values):
        if not self.searchUsersByUsername(tuple(values.split(','))[0]):
            self.c.execute(f'''INSERT INTO users(username,fName,sName,emailAddress,password,admin)
                  VALUES(?, ?, ?, ?, ?, ?)''', tuple(values.split(',')))
            self.conn.commit()
            return
        else:
            return 'user already exists'

    def updateUser(self, param, value, username):
        self.c.execute(f'''UPDATE users SET {param} = "{value}" WHERE username = "{username}";''')
        self.conn.commit()
        return

    def searchUsers(self, email, user):
        self.c.execute(f'''SELECT username, emailAddress FROM users WHERE emailAddress = ? OR username = ?''',
                       (email, user))
        result = self.c.fetchone()
        return result

    def deleteUser(self, user):
        self.c.execute('''DELETE FROM users WHERE username = ?;''', (user,))
        self.conn.commit()
        return

    # license related functions

    def getLicenseInfo(self, license):
        self.c.execute(f'''SELECT * FROM licenses WHERE license = ?''',
                       (license,))
        result = self.c.fetchone()
        return result

    def checkIfLicenseExists(self, license):
        self.c.execute(f'''SELECT * FROM licenses WHERE license = ?''',
                       (license,))
        result = self.c.fetchone()
        return bool(result)

    def checkIfLicenseBound(self, license):
        self.c.execute(f'''SELECT boundToUser FROM licenses WHERE license = ?''',
                       (license,))
        result = self.c.fetchone()
        if not result[0]:
            return False
        else:
            return True

    def checkIfUserHasLicense(self, username):
        self.c.execute(f'''SELECT license FROM licenses WHERE username = ?''',
                       (username,))
        result = self.c.fetchone()
        if result:
            return result[0]
        else:
            return False

    def getUserbyLicense(self, license):
        self.c.execute(f'''SELECT username FROM licenses WHERE license = ?''',
                       (license,))
        result = self.c.fetchone()
        if result:
            return result[0]
        else:
            return None

    def commitLicense(self, license, plan):
        self.c.execute(
            f'''INSERT INTO licenses(license,username,boundtoUser,boundtoDevice,HWID,devicename,nextrenewal,plan,stripeSessionID)
                      VALUES(?, NULL, FALSE, FALSE, NULL, NULL, NULL, ?, "placeholder")''',
            (license, plan))  # needs to be updated to include plan, and validate that plane xists etc.
        self.conn.commit()
        return

    def setLicenseToUnbound(self, license):
        self.c.execute(
            f'''UPDATE licenses SET username = NULL, boundtoUser = False, boundtoDevice = False, HWID = NULL, devicename = NULL WHERE license = ?;''',
            (license,))
        self.conn.commit()
        return

    def setLicenseToUnboundDEVICE(self, license):
        self.c.execute(
            f'''UPDATE licenses SET boundtoDevice = False, HWID = NULL, devicename = NULL WHERE license = ?;''',
            (license,))
        self.conn.commit()
        return

    def setLicenseHWIDandDevice(self, license, hwid, devicename):
        self.c.execute(
            f'''UPDATE licenses SET boundtoDevice = True, HWID = ?, devicename = ? WHERE license = ?;''',
            (hwid, devicename, license,))
        self.conn.commit()
        return

    def updateNextRenewal(self, license, date):
        self.c.execute(f'''UPDATE licenses SET nextrenewal = ? WHERE license = ?;''',
                       (date, license))
        self.conn.commit()
        return

    def updateLicenseKey(self, newlicense, oldlicense):
        self.c.execute(f'''UPDATE licenses SET license = ? WHERE license = ?;''',
                       (newlicense, oldlicense))
        self.conn.commit()
        return

    def getNextRenewal(self, license):
        self.c.execute(f'''SELECT nextrenewal FROM licenses WHERE license = ?''', (license,))
        result = self.c.fetchone()[0]
        if not result or result == "NULL":
            return None
        else:
            return datetime.strptime(result, '%Y-%m-%d %H:%M:%S.%f')

    def getLicenseStripeSessionID(self, license):
        self.c.execute(f'''SELECT stripeSessionID FROM licenses WHERE license = ?''', (license,))
        result = self.c.fetchone()[0]
        return result

    def getAllLicenseWithRenewal(self):
        self.c.execute(f'''SELECT license, nextrenewal FROM licenses WHERE nextrenewal != "None"''')
        result = self.c.fetchall()
        renewaldict = {}
        for value in result:
            renewaldict[value[0]] = datetime.strptime(value[1], '%Y-%m-%d %H:%M:%S.%f')
        return renewaldict

    def bindUsertoLicense(self, license, username):
        if self.checkIfLicenseExists(license):
            if not self.checkIfLicenseBound(license):
                if not self.checkIfUserHasLicense(username):
                    self.c.execute(f'''UPDATE licenses SET boundtoUser = TRUE, username = ? WHERE license = ?;''',
                                   (username, license))
                    print(f'bound {license} to {username}')
                    self.conn.commit()
                    return 'success'
                else:
                    return f'User already has license {self.checkIfUserHasLicense(username)}'
            else:
                return f'That license is already bound to another user'
        else:
            return 'License doesnt exist'

    def getPlanfromLicense(self, license):
        self.c.execute(
            '''SELECT plans.* FROM plans JOIN licenses ON licenses.plan = plans.name WHERE licenses.license = ?;''',
            (license,))
        result = self.c.fetchone()
        resultdict = {"name": result[0],
                      "renewalinterval": result[1],
                      "renewalprice": result[2]}
        return resultdict

    def getLicensesfromPlan(self, plan):
        self.c.execute(
            '''SELECT license FROM licenses where plan =?;''',
            (plan,))
        result = self.c.fetchall()
        return result

    def findBoundLicensesOfGivenPlan(self, plan):
        self.c.execute(
            '''SELECT license FROM licenses where plan =? and boundToUser = 1;''',
            (plan,))
        result = self.c.fetchall()
        return result

    def deleteLicensesOfGivenPlan(self, plan):
        self.c.execute('''DELETE FROM licenses WHERE plan = ?;''', (plan,))
        self.conn.commit()
        return

    def deleteLicense(self, license):
        self.c.execute('''DELETE FROM licenses WHERE license = ?;''', (license,))
        self.conn.commit()
        return

    # plan related functions

    def getPlanInfo(self, name):
        self.c.execute(f'''SELECT * FROM plans WHERE name = "{name}";''')
        result = self.c.fetchone()
        if not result:
            return None
        else:
            return result

    def createPlan(self, name, interval, amount):
        if not self.getPlanInfo(name):
            self.c.execute(f'''INSERT INTO plans(name,interval,amount)
                  VALUES(?, ?, ?)''', (name, interval, amount))
            self.conn.commit()
            return
        else:
            return 'Plan already exists'

    def deletePlan(self, plan):
        self.c.execute('''DELETE FROM plans WHERE name = ?;''', (plan,))
        self.conn.commit()
        return

