from flask import render_template, request, redirect
from flask import Flask
from app import app
from .forms import SearchForm
import requests
import json
import codecs

#Routes Index Page
@app.route('/')
@app.route('/index')
@app.route('/index/')
def index():
    return render_template("index.html",
                           title='Home')

#Routes About Page
@app.route('/about')
@app.route('/about/')
def about():
    return render_template("about.html",
                           title='About')




