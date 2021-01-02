from flask import Flask, render_template, redirect, url_for, request

#https://realpython.com/introduction-to-flask-part-2-creating-a-login-page/

app = Flask(__name__)

@app.route('/')
def index():
    return render_template('index.html')

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

@app.route('/signup')
def signup():
    return 'maintenance'

# @app.route('/singup', methods=['GET', 'POST'])
# def login():
#     error = None
#     if request.method == 'POST':
#         #perfom regex to ensure shit is good
#         if request.form['username'] != 'admin' or request.form['password'] != 'admin':
#             error = 'Invalid Credentials. Please try again.'
#         else:
#             return redirect(url_for('home'))
#     return render_template('login.html', error=error)


if __name__ == '__main__':
    app.run()
