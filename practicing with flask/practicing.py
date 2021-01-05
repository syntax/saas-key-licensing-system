from flask import Flask, render_template, redirect, url_for, request
import re

#https://realpython.com/introduction-to-flask-part-2-creating-a-login-page/

app = Flask(__name__)

@app.route('/')
def index():
    return render_template('home.html')

@app.route('/home')
def home():
    return 'success'

@app.route('/login', methods=['GET', 'POST'])
def login():
    error = None
    if request.method == 'POST':
        print(request.form)
        if request.form['username'] != 'admin' or request.form['password'] != 'admin':
            error = 'Invalid Credentials. Please try again.\nIf you do not yet have an account, you can sign up with the above link.'
        else:
            print('redirectign')
            return redirect(url_for('home'))
    return render_template('login.html', error=error)

@app.route('/signup', methods=['GET', 'POST'])
def signup():
    mailregex = '^[a-z0-9]+[\._]?[a-z0-9]+[@]\w+[.]\w{2,3}$'
    pwregex = "^(?=.*[a-z])(?=.*[A-Z])(?=.*\d)(?=.*[@$!%*?&])[A-Za-z\d@$!%*?&]{8,}$"
    error = None
    if request.method == 'POST':
        print(request.form)
        #perfom regex to ensure shit is good
        if not re.search(mailregex,request.form['email']):
            error = 'Email Invalid'
        elif not re.search(pwregex, request.form['password']):
            error = 'Password invalid. Must be 8+ characters, including at least one upper-case letter, lower-case letter, number and special character.'
        # else:
        #     return redirect(url_for('home'))
    return render_template('signup.html', error=error)


if __name__ == '__main__':
    app.run()
