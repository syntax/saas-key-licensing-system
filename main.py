from flask import Flask, render_template, redirect, url_for, request, abort, jsonify, make_response, send_from_directory
from flask_login import LoginManager, UserMixin, login_required, login_user, logout_user, current_user
import re
from api import Database
import utils
import os
import time
from functools import wraps
import datetime
import json

class Renewal:
    def __init__(self, key):
        self.renewdate = self.getRenewalDate(key)
        self.renewamount = None
        self.renewinterval = None

        #running of this function should result in the last two being defined.
        self.getRenewalInfoFromPlan(key)

    def getRenewalDate(self, key):
        db = Database()
        dbdate = db.getNextRenewal(key)
        return dbdate

    def commitRenewdatetoDatabase(self, key):
        dbconn = Database()
        dbconn.updateNextRenewal(key, self.renewdate)
        dbconn.closeConnection()
        return

    def getRenewalInfoFromPlan(self, key):
        db = Database()
        planinfo = db.getPlanfromLicense(key)
        self.renewamount = float(planinfo['renewalprice'])
        self.renewinterval = int(planinfo['renewalinterval'])
        return planinfo

    def incrementRenewalDate(self):
        if self.renewdate and self.renewdate != 'Error reading DB':
            self.renewdate = self.renewdate + datetime.timedelta(days=self.renewinterval)
            return self.renewdate

    def initalRenewalIncrement(self,key):
        print(self.renewdate)
        if not self.renewdate:
            self.renewdate = datetime.datetime.now()
            self.incrementRenewalDate()
            self.commitRenewdatetoDatabase(key)
            return
        else:
            return 'Not inital'
    
class License:
    #this is a class that describes the license in context of the user its bound to, only.
    def __init__(self,owner):
        self.owner = owner
        self.hwid = None
        self.boundtodevice = False
        self.devicename = None
        self.renewal = None

        self.key = self.loadUserLicense()
        #self.exists is necessary as self.key being None cannot necessarily be represented in conitional statements (due to str dunder), otherwise.
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
            self.renewal = Renewal(self.key)
            return license



class User(UserMixin):
    def __init__(self, username, fname, sname, email, password, couldHaveLicense = True):
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
        #probably needs to be implemented with some sort of ajax on the html client side to prevent it from just having the entire page render again
        #will need to do things such as unbinding from device, as well, keep this in consideration!
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
        super().__init__(username, fname, sname, email, password, couldHaveLicense = False)
        self.isadmin = True


app = Flask(__name__)
app.secret_key = os.urandom(24) #secret key for encoding of session on the webapp

login_manager = LoginManager(app)
login_manager.login_view = "login"


@login_manager.user_loader
def load_user(username):
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
    current_user.unbindLicense()
    return redirect(url_for('dashboard'))

# front end
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
                if current_user.getAdminPerms():
                    return redirect(url_for('admindash'))
                else:
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
    if not current_user.getAdminPerms():
        lerror = None
        if request.method == 'POST' and request.form['licenseid'] != '':
            temp = Database()
            result = temp.bindUsertoLicense(request.form['licenseid'],current_user.id)
            if result == "success":
                current_user.license.loadUserLicense()
                if not current_user.license.renewal.getRenewalDate(current_user.license.key):
                    current_user.license.renewal.initalRenewalIncrement(current_user.license.key)
            else:
                lerror = result
                print(f'ERROR: {lerror}')
    
            return redirect(url_for('dashboard')) #https://www.youtube.com/watch?v=JQFeEscCvTg&ab_channel=DaveHollingworth
    
        return render_template('dashboard.html', lerror=lerror)
    else:
        return redirect(url_for('admindash'))


@app.route("/dashboard/account", methods=['GET', 'POST'])
@login_required
def dashboardaccount():
    if not current_user.getAdminPerms():
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
    else:
        return redirect(url_for('admindash'))

@app.route("/admin/dashboard", methods=['GET', 'POST'])
@login_required
def admindash():
    #https://www.w3schools.com/howto/howto_js_sort_table.asp for the tables when being implemented
    if current_user.getAdminPerms():
        return render_template('admindash.html')
    else:
        reason = f'Insufficient permissions.'
        return render_template('redirect.html', reason=reason)

@app.route("/admin/dashboard/users", methods=['GET', 'POST'])
@login_required
def adminusers():
    if current_user.getAdminPerms():
        if request.method == "POST":
            try:
                db = Database()
                if db.checkIfUserHasLicense(request.form['delete']) != False:
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
            if dbattempt != False:
                user.append(dbattempt)
            else:
                user.append(None)
            users.append(user)
        db.closeConnection()
        return render_template('adminusers.html',users=users)
    else:
        reason = f'Insufficient permissions.'
        return render_template('redirect.html', reason=reason)

@app.route("/admin/dashboard/licenses", methods=['GET', 'POST'])
@login_required
def adminlicenses():
    if current_user.getAdminPerms():
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
                    return send_from_directory(directory=app_config['UPLOAD_DIRECTORY'], filename=filename,
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
        return render_template('adminlicenses.html',licenses=licenses, plans = plans)
    else:
        reason = f'Insufficient permissions.'
        return render_template('redirect.html', reason=reason)

@app.route("/admin/dashboard/plans", methods=['GET', 'POST'])
@login_required
def adminplans():
    if current_user.getAdminPerms():
        if request.method == 'POST':
            try:
                if not 'delete' in request.form:
                    db = Database()
                    db.createPlan(request.form['name'], request.form['days'], request.form['price'])
                    db.closeConnection()

                    return redirect(url_for('adminplans'))
                else:
                    db = Database()
                    if db.findBoundLicensesOfGivenPlan(request.form['delete']) != []:
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
        return render_template('adminplans.html',plans=plans, reason= None)
    else:
        reason = f'Insufficient permissions.'
        return render_template('redirect.html', reason=reason)

@app.route("/getTime", methods=['GET'])
def getTime():
    print("browser time: ", request.args.get("time"))
    print("server time : ", time.strftime('%A %B, %d %Y %H:%M:%S'));
    return "Done"

#API speicifc functions

@app.errorhandler(404)
def not_found():
    return make_response(jsonify({'error': 'not found'}), 404)


@app.errorhandler(400)
def not_found():
    return make_response(jsonify({'error': 'malformed syntax, seek docs'}), 404)


@app.route('/api/v1/licenses/<licenseid>', methods=['GET','POST'])
def get_specific_license(licenseid):
    try:
        if request.headers['api_key'] == app_config['api_key']:
            if request.method == "GET":
                try:
                    db = Database()
                    result = db.getLicenseInfo(licenseid)
                    licensedict = {
                            "lickey":result[0],
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
                    if "HWID" and "device" in request.json:
                        db = Database()
                        if not request.json["HWID"] and not request.json["device"]:
                            db.setLicenseToUnboundDEVICE(licenseid)
                        else:
                            db.setLicenseHWIDandDevice(licenseid,request.json["HWID"],request.json["device"])

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

                        return jsonify({"status":"updated","license": licensedict})
                    else:
                        return jsonify({"status": "malformed request in post, needs HWID and device"})

        else:
            return jsonify({"status": "unauthorised"})
    except:
        return jsonify({"status": "fatal error, perhaps malformed request"})

# @app.route('/api/v1/licenses', methods=['POST'])
# def create_license():
#     if not request.json or not {'first_name', 'last_name', 'email', 'pw', 'license_key','active_status','hwid_identifier','devicename'}.issubset(set(request.json)):
#         abort(400) #either not all params provided, or not posted correctly
#     else:
#         formattedjson = ','.join(list(request.json.values()))
#         dbtemp = Database()
#         try:
#             dbtemp.addToTable_wholerow(formattedjson)
#             dbtemp.closeConnection()
#             return jsonify({'license': request.json}), 201
#         except Exception as e: #closes connection incase of issue writing to db, as to not present later issues
#             print(e)
#             dbtemp.closeConnection()
#             abort(500)


# @app.route('/api/v1/licenses/hwid/<int:licenseid>', methods=['POST'])
# def update_hwid(licenseid):
#     if not request.json or not {'active_status','hwid_identifier','devicename'}.issubset(set(request.json)):
#         abort(400) #malformed request syntax
#     else:
#         tempdb = Database()
#         try:
#             hwid = request.json['hwid_identifier']
#             device = request.json['devicename']
#             active = request.json['active_status']
#             tempdb.hwidAndDeviceToTable(licenseid,hwid,device,active)
#             license = tempdb.getFromTable(licenseid)
#             tempdb.closeConnection()
#             return jsonify({'status_code':'success','license': license}), 201
#         except Exception as e:  # closes connection incase of issue writing to db, as to not present later issues
#             print(e)
#             tempdb.closeConnection()
#             abort(500)


if __name__ == '__main__':
    with open('config.json','r') as configfile:
        app_config = json.load(configfile)
    db = Database()
    db.create()
    app.run()
