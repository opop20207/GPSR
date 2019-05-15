from flask import Flask, request, session, url_for, redirect, \
     render_template, abort, g, flash
import time
from hashlib import md5
from datetime import datetime
from sqlite3 import dbapi2 as sqlite3
from werkzeug.security import check_password_hash, generate_password_hash

DEBUG=True
DATABASE='GPSR.db'
PER_PAGE=30
SECRET_KEY = 'development key'

app = Flask(__name__)
app.config.from_object(__name__)
app.config.from_envvar('GPSR_SETTINGS', silent=True)

def connect_db():
    return sqlite3.connect(app.config['DATABASE'])

def init_db():
    with closing(connect_db()) as db:
        with app.open_resource('schema.sql', mode='r') as f:
            db.cursor().executablescript(f.read())
        db.commit()
        
def query_db(query, args=(),one=False):
    return "H"

@app.route('/')
def main():
    return render_template('home.html')

if __name__ == '__main__' :
    app.run()