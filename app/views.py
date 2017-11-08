
from flask import render_template, request, redirect, session, url_for
from flask import send_from_directory, abort
from flask import Flask

from functools import wraps

from app import app

import pymysql.cursors
import hashlib
import os, sys, stat
from werkzeug.utils import secure_filename

conn = pymysql.connect(host=app.config['DBHOST'],
                       user=app.config['DBUSER'],
                       password=app.config['DBPASS'],
                       db=app.config['DBNAME'],
                       charset='utf8mb4',
                       cursorclass=pymysql.cursors.DictCursor)

def login_required(f):
    @wraps(f)
    def dec(*args, **kwargs):
        if not 'username' in session:
            return redirect(url_for('login'))
        return f(*args, **kwargs)
    return dec

def authenticated():
    return "username" in session

def get_fname():
    if not authenticated():
        return ""
    if 'fname' in session:
        return session['fname']
    uname = session['username']
    cursor = conn.cursor()
    q = 'SELECT fname FROM person WHERE uname = %s'
    cursor.execute(q, (uname))
    result = cursor.fetchone()
    session['fname'] = result['fname']
    return session['fname']

#Routes Index Page
@app.route('/')
def index():
    return render_template("index.html", title='PriCoSha', isAuthenticated=authenticated(), fname=get_fname())

#Routes About Page
@app.route('/about/')
def about():
    return render_template("about.html", title='About', isAuthenticated=authenticated(), fname=get_fname())

#Routes Login Page
@app.route('/login')
@app.route('/login/')
def login():
    return render_template("login.html", title='Login')

#Routes Register Page
@app.route('/register')
@app.route('/register/')
def register():
    return render_template("register.html", title='Register')

#Authenticates the login
@app.route('/loginAuth', methods=['GET', 'POST'])
def loginAuth():
    #grabs information from the forms
    username = request.form['username']
    password = request.form['password']
        
    #cursor used to send queries
    cursor = conn.cursor()
    #executes query
    query = 'SELECT * FROM person WHERE uname = %s and password = %s'
    cursor.execute(query, (username, hashlib.md5(password.encode('utf-8')).hexdigest()))
    #stores the results in a variable
    data = cursor.fetchone()
    #use fetchall() if you are expecting more than 1 data row
    cursor.close()
    error = None
    if(data):
        #creates a session for the the user
        #session is a built in
        session['username'] = username
        return redirect(url_for('home'))
    else:
        #returns an error message to the html page
        error = 'Invalid username or password.'
        return render_template('login.html', error=error)

#Authenticates the register
@app.route('/registerAuth', methods=['GET', 'POST'])
def registerAuth():
    #grabs information from the forms
    username = request.form['username']
    password = request.form['password']
    passconf = request.form['pass-conf']
    if password != passconf:
        error = "Passwords do not match."
        return render_template('register.html', error=error)
    fname = request.form['fname']
    lname = request.form['lname']
    #cursor used to send queries
    cursor = conn.cursor()
    #executes query
    query = 'SELECT * FROM person WHERE uname = %s'
    cursor.execute(query, (username))
    #stores the results in a variable
    data = cursor.fetchone()
    #use fetchall() if you are expecting more than 1 data row
    error = None
    if(data):
        #If the previous query returns data, then user exists
        error = username + " is taken. Try another."
        return render_template('register.html', error = error)
    else:
        ins = 'INSERT INTO person (uname, password, fname, lname) VALUES(%s, %s, %s, %s)'
        cursor.execute(ins, (username, hashlib.md5(password.encode('utf-8')).hexdigest(), fname, lname))
        conn.commit()
        cursor.close()
        session['username'] = username
        return redirect(url_for('home'))

def retrieveData():
    username = session['username']
    cursor = conn.cursor();
    query = 'SELECT date, name, file_path FROM content WHERE uname = %s ORDER BY date DESC'
    cursor.execute(query, (username))
    data = cursor.fetchall()
    query = 'SELECT fname FROM person WHERE uname = %s'
    cursor.execute(query, (username))
    data2 = cursor.fetchone()
    cursor.close()
    return {"username": username, "posts": data, "fname": data2['fname']}

#Routes Home Page Once Logged In
@app.route('/home')
@login_required
def home():
    data = retrieveData()
    uname = session['username']
    return render_template('home.html', username=uname, posts=data["posts"], fname=get_fname())

@app.route('/feed')
@login_required
def feed():
    uname = session['username']
    cursor = conn.cursor()
    q =  '(SELECT DISTINCT date, name, file_path\
          FROM content NATURAL JOIN share NATURAL JOIN member\
          WHERE member = %s)\
          UNION\
          (SELECT date, name, file_path\
          FROM content \
          WHERE is_pub or uname = %s)\
          ORDER BY date desc'
    cursor.execute(q, (uname, uname))
    data = cursor.fetchall()
    cursor.close()
    return render_template('home.html', username=uname, posts=data, fname=get_fname())


#Logging out
@app.route('/logout')
def logout():
    session.pop('fname')
    session.pop('username')
    return redirect('/')

#Posting
@app.route('/post', methods=['GET', 'POST'])
@login_required
def post():
    uname = session['username']
    cursor = conn.cursor();
    cname = request.form['name']
    photo = request.files['file']
    if photo:
        filename = secure_filename(photo.filename)
        #os.chmod(app.config["PHOTO_DIRECTORY"], 0o777)
        photo.save(os.path.join(app.config["PHOTO_DIRECTORY"], filename))
        q = 'INSERT INTO content(name, file_path, uname) VALUES(%s, %s, %s)'
        cursor.execute(q, (cname, filename, uname))
    else:
        q = 'INSERT INTO content(name, uname) VALUES (%s, %s)'
        cursor.execute(q, (cname, uname))
    conn.commit()
    cursor.close()
    return redirect(url_for('home'))

# Retrieve user photos only if logged in
@app.route('/content/<path:filename>')
def retrieve_file(filename):
    if not authenticated():
        abort(404)
    uname = session['username']
    cursor = conn.cursor()
    q = "SELECT file_path FROM content WHERE uname = %s AND file_path = %s"
    cursor.execute(q, (uname, filename))
    res = cursor.fetchone()
    if res:
        return send_from_directory(app.config['PHOTO_DIRECTORY'], filename)
    else:
        abort(404)


#Searching
@app.route('/search', methods=['GET', 'POST'])
def search():
    username = session['username']
    cursor = conn.cursor()
    searchQuery = request.form['query']
    query = 'SELECT date, name FROM content WHERE uname = %s AND name LIKE "\%%s" ORDER BY date DESC'
    cursor.execute(query, (searchQuery))
    data = cursor.fetchone()
    cursor.close()
    return render_template("search_results.html", posts=data)
