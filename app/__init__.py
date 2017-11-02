from flask import Flask
from flask_bootstrap import Bootstrap

app = Flask(__name__)
Bootstrap(app)
app.config.from_object('config')
app.jinja_env.auto_reload = True

from app import views
import pymysql.cursors
