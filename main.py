from flask import Flask, render_template, redirect, url_for, request, abort, jsonify, make_response, flash
from flask_login import LoginManager, UserMixin, login_required, login_user, logout_user, current_user
import re
from api import Database
import os
import time

app = Flask(__name__)
app.secret_key = os.urandom(24) #secret key for encoding of session on the webapp

login_manager = LoginManager(app)
login_manager.login_view = "login"

class User(UserMixin):
    def __init__(self, username, fname, sname, email, password):
         self.id = username
         self.fname = fname
         self.sname = sname
         self.email = email
         self.password = password
         self.authenticated = False
         self.license = None

    #need to add a function to check if a user has a license on load of the user!
    def loadUserLicense(self):
        db = Database()
        license = db.checkIfUserHasLicense(self.id)
        if not license:
            return None
        else:
            self.license = license
            return license


class AdministativeUser(User):
   pass

@login_manager.user_loader
def load_user(username):
    dbconnection = Database()
    result = dbconnection.searchUsersByUsername(username)
    dbconnection.closeConnection()
    print(f'loading user {result[0]}')
    if result:
        return User(result[0],result[1],result[2],result[3],result[4])
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
            #needs to apply hasing to this section, currently all done in plain txt
            if request.form['password'] == result[4]:
                user = load_user(request.form['username'])
                login_user(user)
                print(f'user {result[0]} logging in!')
                return redirect(url_for('dashboard'))
            else:
                error = 'Invalid password!'
    return render_template('login.html', error=error)

@app.route('/signup', methods=['GET', 'POST'])
def signup():

    mailregex = "^[a-z0-9]+[\._]?[a-z0-9]+[@]\w+[.]\w{2,3}$"
    pwregex = "^(?=.*[a-z])(?=.*[A-Z])(?=.*\d)(?=.*[@$!%*?&])[A-Za-z\d@$!%*?&]{8,}$"
    nospacesregex = "^\\S*$"
    error = None

    if current_user.is_authenticated:
        return redirect(url_for('dashboard'))
    if request.method == 'POST':
        temp = Database()
        if not ' ' in request.form['name'] or len(request.form['name'].split(' ')) != 2:
            error = 'Your first and surname, with a space inbetween!'
        elif not re.search(nospacesregex, request.form['username']):
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
            temp.addToUsers(f'''{request.form['username']},{request.form['name'].split()[0]},{request.form['name'].split()[1]},{request.form['email']},{request.form['password']},FALSE''')
            print('Sucessuflly commited to database.')
            user = load_user(request.form['username'])
            login_user(user)
            temp.closeConnection()
            return redirect(url_for('dashboard'))

    return render_template('signup.html', error=error)

@app.route("/logout")
@login_required
def logout():
    reason=f'logging out of account {current_user.id}!'
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
            current_user.loadUserLicense()
            print(current_user.license)
        else:
            lerror = result
            print(f'ERROR: {lerror}')

    return render_template('dashboard.html', lerror=lerror)

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
