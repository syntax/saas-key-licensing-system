from flask import Flask, render_template, redirect, url_for, request, abort, jsonify, make_response, send_from_directory
from flask_login import LoginManager, UserMixin, login_required, login_user, logout_user, current_user
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address
import re
from api import Database
import monitor
import utils
import os
import time
import datetime
import json
import threading
import random
import csv


class Renewal:
    def __init__(self, key):
        self.renewdate = self.getRenewalDate(key)
        self.renewamount = None
        self.renewinterval = None

        # running of this function should result in the last two being defined.
        self.getRenewalInfoFromPlan(key)

    def getRenewalDate(self, key):
        # gets date of the next renewal given a key
        db = Database()
        dbdate = db.getNextRenewal(key)
        return dbdate

    def commitRenewdatetoDatabase(self, key):
        # commits a renewal date to db following a change within the class
        dbconn = Database()
        dbconn.updateNextRenewal(key, self.renewdate)
        dbconn.closeConnection()
        return

    def getRenewalInfoFromPlan(self, key):
        # gets all information regarding a licenses renewal through its plan attribute
        db = Database()
        planinfo = db.getPlanfromLicense(key)
        self.renewamount = float(planinfo['renewalprice'])
        self.renewinterval = int(planinfo['renewalinterval'])
        return planinfo

    def incrementRenewalDate(self):
        # increments the renewal date the correct period in the case the license is renewed
        if self.renewdate and self.renewdate != 'Error reading DB':
            self.renewdate = self.renewdate + datetime.timedelta(days=self.renewinterval)
            return self.renewdate

    def initalRenewalIncrement(self, key):
        # performs the inital renewal increment, adding correct period of days on its first bind
        if not self.renewdate:
            self.renewdate = datetime.datetime.now()
            self.incrementRenewalDate()
            self.commitRenewdatetoDatabase(key)
            return
        else:
            return 'Not inital'


class License:
    # this is a class that describes the license in context of the user its bound to, only.
    def __init__(self, owner):
        self.owner = owner
        self.hwid = None
        self.boundtodevice = False
        self.devicename = None
        self.renewal = None

        self.key = self.loadUserLicense()
        # self.exists is necessary as self.key being None cannot necessarily be represented in conitional statements (due to str dunder), otherwise.
        if self.key:
            self.exists = True
            self.renewal = Renewal(self.key)
        else:
            self.exists = False

    def __str__(self):
        return str(self.key)

    def __repr__(self):
        return self.__str__()

    def loadUserLicense(self):
        # loads all license related information in relation to a user, when given a user.
        db = Database()
        license = db.checkIfUserHasLicense(self.owner)
        if not license:
            db.closeConnection()
            self.key = None
            self.exists = False
            return None
        else:
            self.key = license
            self.exists = True
            self.renewal = Renewal(self.key)

            licenseinfo = db.getLicenseInfo(license)
            if licenseinfo[3] == 1:
                self.boundtodevice = True
            else:
                self.boundtodevice = False
            self.hwid = licenseinfo[4]
            self.devicename = licenseinfo[5]
            return license

    def unbindDevice(self):
        # sets the device the license is bound to to none
        if not self.key:
            return 'No license currently bound to account'
        else:
            if not self.boundtodevice:
                return 'License not currently bound to a device to unbind from'
            else:
                db = Database()
                db.setLicenseToUnboundDEVICE(self.key)
                db.closeConnection()
                self.hwid = None
                self.devicename = None
                self.boundtodevice = False
                return

    def rescramble(self):
        # rescrambles the key identifier to a unique value
        if not self.key:
            return 'No license currently bound to account'
        else:
            while True:
                license = utils.generatekey(random_chars=16)
                # 79586 6110994640 0884391936 combinations
                conn = Database()
                if conn.checkIfLicenseExists(license):
                    continue
                else:
                    print(f'found unused license value {license}')
                    self.unbindDevice()
                    conn.updateLicenseKey(license, self.key)
                    self.loadUserLicense()
                    conn.closeConnection()
                    return license
        return


class User(UserMixin):
    def __init__(self, username, fname, sname, email, password, couldHaveLicense=True):
        self.id = username
        self.fname = fname
        self.sname = sname
        self.email = email
        self.hashdpassword = password
        self.authenticated = False
        self.isadmin = False

        if couldHaveLicense:
            self.license = License(self.id)

    def __str__(self):
        return self.id

    def unbindLicense(self):
        # unbinds a license from a user's account, called by an ajax function.
        if self.license:
            db = Database()
            db.setLicenseToUnbound(self.license.key)
            db.closeConnection()
            self.license = None
            return
        else:
            return 'No License bound previously'

    def getAdminPerms(self):
        return self.isadmin


class AdministativeUser(User):
    def __init__(self, username, fname, sname, email, password):
        super().__init__(username, fname, sname, email, password, couldHaveLicense=False)
        self.isadmin = True


app = Flask(__name__)
# secret key for encoding of session on the webapp
app.secret_key = os.urandom(24)

login_manager = LoginManager(app)
login_manager.login_view = "login"

limiter = Limiter(
    app=app,
    key_func=get_remote_address,
    default_limits=["20 per second"],
)


@login_manager.user_loader
def load_user(username):
    # function for loading all appropriate user data, and the specific user type, on login
    dbconnection = Database()
    result = dbconnection.searchUsersByUsername(username)
    dbconnection.closeConnection()
    if result:
        if result[5] == "FALSE":
            return User(result[0], result[1], result[2], result[3], result[4])
        else:
            return AdministativeUser(result[0], result[1], result[2], result[3], result[4])
    else:
        return None


# api based functs

@app.route("/unbindaccount")
@login_required
def unbindkey():
    # ajax-called function for unbinding key from a account
    current_user.unbindLicense()
    return redirect(url_for('dashboard'))


@app.route("/unbinddevice")
@login_required
def unbinddevice():
    # ajax-called function for unbinding device from a key
    current_user.license.unbindDevice()
    return redirect(url_for('dashboard'))


@app.route("/rescramblelicense")
@login_required
def rescramblelicense():
    # ajax-called function for rescrambling license identifier
    current_user.license.rescramble()
    return redirect(url_for('dashboard'))


# front end webapp endpoints

@app.route('/favicon.ico')
def getfavicon():
    # returns favicon for any page on the domain
    # otherwise risks returning 500s if this endpoint is not present.
    return send_from_directory(os.path.join(app.root_path, 'static'),
                               'favicon.ico', mimetype='image/vnd.microsoft.icon')


@app.route('/')
def index():
    # front page of website
    return render_template('home.html')


@app.route('/login', methods=['GET', 'POST'])
def login():
    # validates inputs and compares with database
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
                if current_user.getAdminPerms():
                    return redirect(url_for('admindash'))
                else:
                    return redirect(url_for('dashboard'))
            else:
                error = 'Invalid password!'
    return render_template('login.html', error=error)


@app.route('/signup', methods=['GET', 'POST'])
def signup():
    # validates inputs and commits to database
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
        elif not re.search(mailregex, request.form['email']):
            error = 'Email Invalid'
        elif not re.search(pwregex, request.form['password']):
            error = 'Password invalid. Must be 8+ characters, including at least one upper-case letter, lower-case letter, number and special character.'
        elif request.form['password'] != request.form['confirmpassword']:
            error = 'Your passwords do not match.'
        elif temp.searchUsers(request.form['email'],
                              request.form['username']):  # checks if this returns anythng other than NONE
            error = 'An account using that email or username already exists!'
        else:
            hashdpw = utils.hash(request.form['username'], request.form['password'])
            temp.addToUsers(
                f'''{request.form['username']},{request.form['name'].split()[0]},{request.form['name'].split()[1]},{request.form['email']},{hashdpw},FALSE''')
            user = load_user(request.form['username'])
            login_user(user)
            temp.closeConnection()
            return redirect(url_for('dashboard'))

    return render_template('signup.html', error=error)


@app.route("/logout")
@login_required
def logout():
    # logs out of the application
    reason = f'logging out of account {current_user}!'
    logout_user()
    return render_template('redirect.html', reason=reason)


@app.route("/dashboard", methods=['GET', 'POST'])
@login_required
def dashboard():
    # returns user based dashboad
    if not current_user.getAdminPerms():
        lerror = None
        if request.method == 'POST' and request.form['licenseid'] != '':
            temp = Database()
            result = temp.bindUsertoLicense(request.form['licenseid'], current_user.id)
            if result == "success":
                current_user.license.loadUserLicense()
                if not current_user.license.renewal.getRenewalDate(current_user.license.key):
                    current_user.license.renewal.initalRenewalIncrement(current_user.license.key)
            else:
                lerror = result
                print(f'ERROR: {lerror}')

            # redirect appropriate as to avoid POST callbacks
            # explained beautifully here: https://www.youtube.com/watch?v=JQFeEscCvTg&ab_channel=DaveHollingworth
            return redirect(url_for('dashboard'))

        return render_template('dashboard.html', lerror=lerror)
    else:
        return redirect(url_for('admindash'))


@app.route("/dashboard/account", methods=['GET', 'POST'])
@login_required
def dashboardaccount():
    # allows for user account settings to be edited following their arrival at their dashboard
    if not current_user.getAdminPerms():
        error = None
        mailregex = r"^[a-z0-9]+[\._]?[a-z0-9]+[@]\w+[.]\w{2,3}$"
        namesregex = r"[a-zA-Z]+"
        pwregex = "^(?=.*[a-z])(?=.*[A-Z])(?=.*\d)(?=.*[@$!%*?&])[A-Za-z\d@$!%*?&]{8,}$"

        if request.method == 'POST':
            form = request.form.to_dict()
            if utils.hash(current_user.id, form['cpassword']) == current_user.hashdpassword:
                for regex, value, potentialerror in zip([namesregex, namesregex, mailregex],
                                                        [form['fname'], form['sname'], form['email']],
                                                        ["Invalid first name", "Invalid surname", "Invalid email"]):
                    if not re.fullmatch(regex, value):
                        return render_template('dashboardaccount.html', error=potentialerror)
                if request.form['newpassword']:
                    if not re.fullmatch(pwregex, form['newpassword']):
                        return render_template('dashboardaccount.html', error='Not a valid password!')
                    else:
                        form['newpassword'] = utils.hash(current_user.id, request.form['newpassword'])

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
    else:
        return redirect(url_for('admindash'))


@app.route("/admin/dashboard", methods=['GET', 'POST'])
@login_required
def admindash():
    # shows overview page with a selection of interesting stats
    if current_user.getAdminPerms():
        statsdict = utils.gatherStatistics()
        randomstats = [[statsdict[value], value] for value in random.sample(list(statsdict), 3)]
        return render_template('admindash.html', stats=randomstats)
    else:
        reason = f'Insufficient permissions.'
        return render_template('redirect.html', reason=reason)


@app.route("/admin/dashboard/users", methods=['GET', 'POST'])
@login_required
def adminusers():
    # endpoint for reaching users table
    if current_user.getAdminPerms():
        # in the case where users are attempting to be deleted (POST)
        if request.method == "POST":
            try:
                db = Database()
                if db.checkIfUserHasLicense(request.form['delete']):
                    db.setLicenseToUnbound(db.checkIfUserHasLicense(request.form['delete']))
                db.deleteUser(request.form['delete'])
                db.closeConnection()

                return redirect(url_for('adminusers'))

            except:
                return redirect(url_for("adminusers"))

        db = Database()
        tempusers = db.getAll('users')
        users = []
        for user in tempusers:
            user = list(user)
            dbattempt = db.checkIfUserHasLicense(user[0])
            if dbattempt:
                user.append(dbattempt)
            else:
                user.append(None)
            users.append(user)
        db.closeConnection()
        return render_template('adminusers.html', users=users)
    else:
        reason = f'Insufficient permissions.'
        return render_template('redirect.html', reason=reason)


@app.route("/admin/dashboard/licenses", methods=['GET', 'POST'])
@login_required
def adminlicenses():
    # endpoint for reaching licenses table
    if current_user.getAdminPerms():
        # in the case where licenses are attempting to be made / deleted (POST)
        if request.method == 'POST':
            try:
                if not 'delete' in request.form:
                    arr = []
                    for _ in range(int(request.form['amount'])):
                        key = utils.createLicense(request.form['plans'])
                        arr.append(key)

                    filename = 'gennedkeys.txt'
                    with open(f'temp/{filename}', 'w') as output:
                        for key in arr:
                            output.write("%s\n" % key)

                    # return redirect(url_for('dashboard'))
                    return send_from_directory(directory=app_config['UPLOAD_DIRECTORY_TEMP'], filename=filename,
                                               as_attachment=True)
                else:
                    db = Database()
                    db.deleteLicense(request.form['delete'])
                    db.closeConnection()
                    return redirect(url_for('adminlicenses'))
            except:
                return redirect(url_for('adminlicenses'))

        db = Database()
        licenses = db.getAll('licenses')
        plans = db.getAll('plans')
        db.closeConnection()
        return render_template('adminlicenses.html', licenses=licenses, plans=plans)
    else:
        reason = f'Insufficient permissions.'
        return render_template('redirect.html', reason=reason)


@app.route("/admin/dashboard/plans", methods=['GET', 'POST'])
@login_required
def adminplans():
    # endpoint for reaching plans table
    if current_user.getAdminPerms():
        # in the case where plans are attempting to be made / deleted (POST)
        if request.method == 'POST':
            try:
                if not 'delete' in request.form:
                    db = Database()
                    db.createPlan(request.form['name'], request.form['days'], request.form['price'])
                    db.closeConnection()

                    return redirect(url_for('adminplans'))
                else:
                    db = Database()
                    if db.findBoundLicensesOfGivenPlan(request.form['delete']):
                        print('cannot delete')
                        db = Database()
                        plans = list(db.getAll('plans'))
                        db.closeConnection()
                        return render_template('adminplans.html', plans=plans,
                                               reason='Cannot delete as a user(s) currently has a license of this plan type bound, delete this license first.')
                    else:
                        db.deleteLicensesOfGivenPlan(request.form['delete'])
                        db.deletePlan(request.form['delete'])
                        db.closeConnection()
                        return redirect(url_for('adminplans'))
            except:
                return redirect(url_for('adminplans'))

        db = Database()
        plans = list(db.getAll('plans'))
        db.closeConnection()
        return render_template('adminplans.html', plans=plans, reason=None)
    else:
        reason = f'Insufficient permissions.'
        return render_template('redirect.html', reason=reason)


@app.route("/admin/dashboard/documentation", methods=['GET', 'POST'])
@login_required
def admindocs():
    # endpoint for accessing documentation
    if current_user.getAdminPerms():
        if request.method == 'POST':
            # in the case where user attempts to download a API wrapper file
            return send_from_directory(directory=app_config['UPLOAD_DIRECTORY_MAIN'], filename='examplerequests.py',
                                       as_attachment=True)
        return render_template('admindocs.html', api_key=app_config['api_key'])
    else:
        reason = f'Insufficient permissions.'
        return render_template('redirect.html', reason=reason)


# API speicifc functions

@app.errorhandler(404)
def not_found(e):
    # error handler in the case of unrecognised endpoint
    return render_template('redirect.html', reason='Unrecognised endpoint.')


@app.errorhandler(400)
def bad_syntax(e):
    # error handler in the case of unrecognised request body, through API
    return make_response(jsonify({'error': 'malformed syntax, seek docs'}), 400)


@app.route('/api/v1/licenses/<licenseid>', methods=['GET', 'POST'])
@limiter.limit("2 per second")
def get_specific_license(licenseid):
    # entire API endpoint which accepts both GET and POST requests
    try:
        if request.headers['api_key'] == app_config['api_key']:
            if request.method == "GET":
                try:
                    db = Database()
                    result = db.getLicenseInfo(licenseid)
                    print(result)
                    licensedict = {
                        "lickey": result[0],
                        "user": result[1],
                        "boundToUser": result[2],
                        "boundToDevice": result[3],
                        "HWID": result[4],
                        "device": result[5],
                        "nextRen": result[6],
                        "planName": result[7]
                    }

                    return jsonify({"license": licensedict})
                except:
                    return jsonify({"license": "could not find license"})
            elif request.method == "POST":
                print(request.json)
                if "HWID" and "device" in request.json:
                    db = Database()
                    if not request.json["HWID"] and not request.json["device"]:
                        db.setLicenseToUnboundDEVICE(licenseid)
                    else:
                        db.setLicenseHWIDandDevice(licenseid, request.json["HWID"], request.json["device"])

                    result = db.getLicenseInfo(licenseid)
                    licensedict = {
                        "lickey": result[0],
                        "user": result[1],
                        "boundToUser": result[2],
                        "boundToDevice": result[3],
                        "HWID": result[4],
                        "device": result[5],
                        "nextRen": result[6],
                        "planName": result[7]
                    }

                    return jsonify({"status": "updated", "license": licensedict})
                else:
                    return jsonify({"status": "malformed request in post, needs HWID and device"})

        else:
            return jsonify({"status": "unauthorised"})
    except:
        return jsonify({"status": "fatal error, perhaps malformed request"})


if __name__ == '__main__':
    with open('config.json', 'r') as configfile:
        # open and read config file
        app_config = json.load(configfile)

    # initalistaion of the database
    db = Database()
    db.create()

    # creates and runs monitor renewal function on a secondary daemon thread
    monitorfunct = threading.Thread(name='monitor', target=monitor.monitorRenewals, daemon=True)
    monitorfunct.start()

    # creates and runs monitor stats function on a secondary daemon thread
    monitorstats = threading.Thread(name='monitorstats', target=monitor.monitorGraphs, daemon=True)
    monitorstats.start()

    # runs flask application on main thread
    app.run()
