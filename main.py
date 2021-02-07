from flask import Flask, render_template, redirect, url_for, request, abort, jsonify, make_response, flash
from flask_login import LoginManager, UserMixin, login_required, login_user, logout_user, current_user
import re
from api import Database
import utils
import os
import time

app = Flask(__name__)
app.secret_key = os.urandom(24) #secret key for encoding of session on the webapp

login_manager = LoginManager(app)
login_manager.login_view = "login"


class RenewalDate():
    def __init__(self):
        self.renewdate = None

class License():
    #this is a class that describes the license in context of the user its bound to, only.
    def __init__(self,owner):
        self.owner = owner
        self.hwid = None
        self.boundtodevice = False
        self.devicename = None
        self.renewdate =None

        self.key = self.loadUserLicense()
        #self.exists is necessary as self.key being None cannot necessarily be represented in conitional statements (due to str dunder), otherwise.
        if self.key != None:
            self.exists = True
            self.renewdate = self.getRenewalDate()
        else:
            self.exists = False

    def __str__(self):
        return str(self.key)

    def __repr__(self):
        return self.__str__(self)

    def loadUserLicense(self):
        db = Database()
        license = db.checkIfUserHasLicense(self.owner)
        db.closeConnection()
        if not license:
            self.key = None
            self.exists = False
            return None
        else:
            self.key = license
            self.exists = True
            return license

    def getRenewalDate(self): #consider making this a whole new class, lots of attrs and other things that can be done about it tbh
        db = Database()
        dbdate = db.getNextRenewal(self.key)
        return dbdate


class User(UserMixin):
    def __init__(self, username, fname, sname, email, password, couldHaveLicense = True):
         self.id = username
         self.fname = fname
         self.sname = sname
         self.email = email
         self.hashdpassword = password
         self.authenticated = False

         if couldHaveLicense:
            self.license = License(self.id)

    def __str__(self):
        return self.id

class AdministativeUser(User):
    def __init__(self, username, fname, sname, email, password):
        super().__init__(username, fname, sname, email, password, couldHaveLicense = False)


@login_manager.user_loader
def load_user(username):
    dbconnection = Database()
    result = dbconnection.searchUsersByUsername(username)
    dbconnection.closeConnection()
    if result:
        if result[5] == "FALSE":
            print(f'loading user {result[0]}')
            return User(result[0], result[1], result[2], result[3], result[4])
        else:
            print(f'loading admin user {result[0]}')
            return AdministativeUser(result[0], result[1], result[2], result[3], result[4])
    else:
        return None

@app.route('/')
def index():
    return render_template('home.html')


@app.route('/login', methods=['GET', 'POST'])
def login():
    error = None
    if current_user.is_authenticated:
        return redirect(url_for('dashboard'))
    if request.method == 'POST':
        temp = Database()
        result = temp.searchUsersByUsername(request.form['username'])
        temp.closeConnection()
        if not result:
            error = 'No account with that username.\nIf you do not yet have an account, you can sign up with the above link.'
        else:
            hashdpw = utils.hash(request.form['username'], request.form['password'])
            if hashdpw == result[4]:
                user = load_user(request.form['username'])
                login_user(user)
                print(f'user {result[0]} logging in!')
                return redirect(url_for('dashboard'))
            else:
                error = 'Invalid password!'
    return render_template('login.html', error=error)


@app.route('/signup', methods=['GET', 'POST'])
def signup():

    mailregex = r"^[a-z0-9]+[\._]?[a-z0-9]+[@]\w+[.]\w{2,3}$"
    pwregex = r"^(?=.*[a-z])(?=.*[A-Z])(?=.*\d)(?=.*[@$!%*?&])[A-Za-z\d@$!%*?&]{8,}$"
    unameregex = r"^[A-Za-z0-9]+$"
    error = None

    if current_user.is_authenticated:
        return redirect(url_for('dashboard'))
    if request.method == 'POST':
        temp = Database()
        if ' ' not in request.form['name'] or len(request.form['name'].split(' ')) != 2:
            error = 'We require your first and surname, with a space inbetween!'
        elif not re.search(unameregex, request.form['username']):
            error = 'Your username cannot contain any spaces!'
        elif not re.search(mailregex,request.form['email']):
            error = 'Email Invalid'
        elif not re.search(pwregex, request.form['password']):
            error = 'Password invalid. Must be 8+ characters, including at least one upper-case letter, lower-case letter, number and special character.'
        elif request.form['password'] != request.form['confirmpassword']:
            error = 'Your passwords do not match.'
        elif temp.searchUsers(request.form['email'],request.form['username']): #checks if this returns anythng other than NONE
            error = 'An account using that email or username already exists!'
        else:
            hashdpw = utils.hash(request.form['username'],request.form['password'])
            temp.addToUsers(f'''{request.form['username']},{request.form['name'].split()[0]},{request.form['name'].split()[1]},{request.form['email']},{hashdpw},FALSE''')
            print('Sucessuflly commited to database.')
            user = load_user(request.form['username'])
            login_user(user)
            temp.closeConnection()
            return redirect(url_for('dashboard'))

    return render_template('signup.html', error=error)


@app.route("/logout")
@login_required
def logout():
    reason = f'logging out of account {current_user}!'
    logout_user()
    return render_template('redirect.html', reason=reason)


@app.route("/dashboard", methods=['GET', 'POST'])
@login_required
def dashboard():
    lerror = None
    if request.method == 'POST' and request.form['licenseid'] != '':
        print('trying to bind')
        temp = Database()
        result = temp.bindUsertoLicense(request.form['licenseid'],current_user.id)
        if result == "success":
            current_user.license.loadUserLicense()
            print(f'bound {current_user.license} to {current_user}')
        else:
            lerror = result
            print(f'ERROR: {lerror}')

    return render_template('dashboard.html', lerror=lerror)


@app.route("/dashboard/account", methods=['GET', 'POST'])
@login_required
def dashboardaccount():
    error = None
    mailregex = r"^[a-z0-9]+[\._]?[a-z0-9]+[@]\w+[.]\w{2,3}$"
    namesregex = r"[a-zA-Z]+"
    pwregex = "^(?=.*[a-z])(?=.*[A-Z])(?=.*\d)(?=.*[@$!%*?&])[A-Za-z\d@$!%*?&]{8,}$"

    if request.method == 'POST':
        form = request.form.to_dict()
        if utils.hash(current_user.id,form['cpassword']) == current_user.hashdpassword:
            for regex, value, potentialerror in zip([namesregex, namesregex, mailregex], [form['fname'], form['sname'], form['email']], ["Invalid first name", "Invalid surname", "Invalid email"]):
                if not re.fullmatch(regex, value):
                    return render_template('dashboardaccount.html', error = potentialerror)
            if request.form['newpassword']:
                if not re.fullmatch(pwregex,form['newpassword']):
                    return render_template('dashboardaccount.html', error = 'Not a valid password!')
                else:
                    form['newpassword'] = utils.hash(current_user.id,request.form['newpassword'])

            db = Database()

            keymap = {"newpassword": "password", "fname": "fName", "sname": "sName", "email": "emailAddress"}
            for k, v in form.items():
                if v != "" and k != "cpassword":
                    db.updateUser(keymap[k], v, current_user.id)
                    
            db.closeConnection()
            return render_template('redirect.html', reason='Successfully commited changes!')
        else:
            error = 'Current password is needed to commit changes and is incorrect/missing'


    return render_template('dashboardaccount.html', error=error)


@app.route("/getTime", methods=['GET'])
def getTime():
    print("browser time: ", request.args.get("time"))
    print("server time : ", time.strftime('%A %B, %d %Y %H:%M:%S'));
    return "Done"


@app.errorhandler(404)
def not_found():
    return make_response(jsonify({'error': 'not found'}), 404)


@app.errorhandler(400)
def not_found():
    return make_response(jsonify({'error': 'malformed syntax, seek docs'}), 404)


@app.route('/api/v1/licenses', methods=['GET'])
def get_licenses():
    pass


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
                        "hwid_identifier": license[6],
                        "device_name": license[7]
                        }
    dbtemp.closeConnection()
    return jsonify({'license': license_dict})


@app.route('/api/v1/licenses', methods=['POST'])
def create_license():
    if not request.json or not {'first_name', 'last_name', 'email', 'pw', 'license_key','active_status','hwid_identifier','devicename'}.issubset(set(request.json)):
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


@app.route('/api/v1/licenses/hwid/<int:licenseid>', methods=['POST'])
def update_hwid(licenseid):
    if not request.json or not {'active_status','hwid_identifier','devicename'}.issubset(set(request.json)):
        abort(400) #malformed request syntax
    else:
        tempdb = Database()
        try:
            hwid = request.json['hwid_identifier']
            device = request.json['devicename']
            active = request.json['active_status']
            tempdb.hwidAndDeviceToTable(licenseid,hwid,device,active)
            license = tempdb.getFromTable(licenseid)
            tempdb.closeConnection()
            return jsonify({'status_code':'success','license': license}), 201
        except Exception as e:  # closes connection incase of issue writing to db, as to not present later issues
            print(e)
            tempdb.closeConnection()
            abort(500)


@app.route('/api/v1/licenses<int:licenseid>', methods=['DELETE'])
def delete_task(licenseid):
    temp = Database()
    try:
        temp.removeFromTable(licenseid)
        temp.closeConnection()
        return jsonify({'status': 'success'})
    except Exception as e:
        print(e)
        temp.closeConnection()
        abort(500)


if __name__ == '__main__':
    db = Database()
    db.create()
    app.run()
