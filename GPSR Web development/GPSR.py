from flask import Flask, request, session, url_for, redirect, \
     render_template, abort, g, flash
import time
from hashlib import md5
from datetime import datetime
from sqlite3 import dbapi2 as sqlite3
from werkzeug.security import check_password_hash, generate_password_hash

#config
Debug=True
DATABASE='GPSR.db'
PER_PAGE='30'
SECRET_KEY = 'development key'

app = Flask(__name__)
app.config.from_object(__name__)

@app.route('/')
def main():
    return render_template('home.html')

if __name__ == '__main__':
    app.run()