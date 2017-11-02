from flask import render_template, request, redirect
from flask import Flask
from app import app
import pymysql.cursors
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




