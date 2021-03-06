from flask import Flask, render_template, request, redirect, session
import pymongo
import dns
import aes

app = Flask(__name__)
app.secret_key = b'_5#y2L"F4Q8z\n\xec]/'


URI = 'mongodb+srv://vhomesgroup:vhomes2019@cluster0.rmikc.mongodb.net/VHomes?retryWrites=true&w=majority'
KEY = 'YpzUpPSQd3NSmz1b'
cipher = aes.AESCipher(KEY)


@app.route('/')
def index():
    session['logged_in'] = False
    return render_template('home.html', logged_in=session.get('logged_in'));


@app.route('/home')
def home():
    return render_template('home.html', logged_in=session.get('logged_in'));

@app.route('/logout')
def logout():
    session['logged_in'] = False
    return render_template('home.html', logged_in=session.get('logged_in'));

@app.route('/contact')
def contact():
    return render_template('contact.html', logged_in=session.get('logged_in'));


@app.route('/locations')
def locations():
    return render_template('locations.html', logged_in=session.get('logged_in'));


@app.route('/services')
def services():
    return render_template('services.html', logged_in=session.get('logged_in'))


@app.route('/signup')
def signup():
    return render_template('signup.html', logged_in=session.get('logged_in'));


@app.route('/signup_success')
def signup_success():
    name = request.args.get('name')
    email = request.args.get('email')
    password = request.args.get('password')

    enc_pass = cipher.encrypt(password)

    inputs = {
        'name': name,
        'email': email,
        'password': enc_pass
    }

    def check_db(email):
        my_client = pymongo.MongoClient(URI)
        my_db = my_client['VHomes']
        my_col = my_db['users']
        user = my_col.find_one({'email': str(email)})
        return user

    def add_to_db(inputs):
        my_client = pymongo.MongoClient(URI)
        my_db = my_client['VHomes']
        my_col = my_db['users']
        my_col.insert_one(inputs)

    if check_db(email) == None:
        add_to_db(inputs)
        response = 'sign up successful!'
        session['logged_in'] = True
        return render_template('signup_success.html', response=response, logged_in=session.get('logged_in'))
    else:
        response = 'email already registered'
        session['logged_in'] = False
        return render_template('signup_unsuccessful.html', response=response, logged_in=session.get('logged_in'))


@app.route('/login')
def login():
    return render_template('login.html', logged_in=session.get('logged_in'))


@app.route('/login_success')
def login_success():
    email = request.args.get('email')
    password = request.args.get('password')

    inputs = {
        'email': email,
        'password': password
    }

    def get_from_db(email, password):
        my_client = pymongo.MongoClient(URI)
        my_db = my_client['VHomes']
        my_col = my_db['users']
        user = my_col.find_one({'email': str(email)})
        dec_pass = cipher.decrypt(str(user['password']))
        if str(user['email']) == email and dec_pass == password:
            return True
        else:
            return False

    if get_from_db(email, password) == False:
        response = 'incorrect username or password'
        session['logged_in'] = False
        return render_template('login_unsuccessful.html', response=response, logged_in=session.get('logged_in'))
    else:
        response = 'logged in as ' + email
        session['logged_in'] = True
        return render_template('login_success.html', response=response, logged_in=session.get('logged_in'))

@app.route('/profile')
def profile():
    return render_template('profile.html', logged_in=session.get('logged_in'))

if __name__ == '__main__':
    app.run()
