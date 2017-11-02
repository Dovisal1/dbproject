from flask import render_template, request, redirect, session, url_for
from flask import Flask
from app import app
import pymysql.cursors
import hashlib
#from .forms import SearchForm
#import requests
#import json
#import codecs

conn = pymysql.connect(host=app.config['DBHOST'],
                       user=app.config['DBUSER'],
                       password=app.config['DBPASS'],
                       db=app.config['DBNAME'],
                       charset='utf8mb4',
                       cursorclass=pymysql.cursors.DictCursor)

#Routes Index Page
@app.route('/')
@app.route('/index/')
def index():
    return render_template("index.html",
                           title='Home')

#Routes About Page
@app.route('/about/')
def about():
    return render_template("about.html",
                           title='About')

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
    cursor.execute(query, (username, hashlib.md5(password).hexdigest()))
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
        error = 'Invalid login or username'
        return render_template('login.html', error=error)

#Authenticates the register
@app.route('/registerAuth', methods=['GET', 'POST'])
def registerAuth():
    #grabs information from the forms
    username = request.form['username']
    password = request.form['password']
        
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
        error = "This user already exists"
        return render_template('register.html', error = error)
    else:
        ins = 'INSERT INTO person VALUES(%s, %s)'
        cursor.execute(ins, (username, hashlib.md5(password).hexdigest()))
        conn.commit()
        cursor.close()
        return render_template('index.html')

#Routes Home Page Once Logged In
@app.route('/home')
def home():
    username = session['username']
    cursor = conn.cursor();
    query = 'SELECT date, name FROM content NATURAL JOIN post WHERE uname = %s ORDER BY date DESC'
    cursor.execute(query, (username))
    data = cursor.fetchall()
    query = 'SELECT fname FROM person WHERE uname = %s'
    cursor.execute(query, (username))
    data2 = cursor.fetchone()
    cursor.close()
    return render_template('home.html', username=username, posts=data, fname=data2)

#Logging out
@app.route('/logout')
def logout():
    session.pop('username')
    return redirect('/')


