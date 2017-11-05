from flask import Flask
from flask_bootstrap import Bootstrap

from datetime import datetime
from ago import human

app = Flask(__name__)
Bootstrap(app)
app.config.from_object('config')
app.jinja_env.auto_reload = True

def time_ago_in_words(time):
    ts = datetime.now() - time
    return human(ts, precision=1)

app.jinja_env.filters['time_ago'] = time_ago_in_words

from app import views
import pymysql.cursors
