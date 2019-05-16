from flask import Flask, request, session, url_for, redirect, \
     render_template, abort, g, flash
import time
from hashlib import md5
from datetime import datetime
from sqlite3 import dbapi2 as sqlite3
from werkzeug.security import check_password_hash, generate_password_hash
from flask.templating import render_template

#settings
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
        
def get_user_id(username):
    chk = g.db.execute('select user_id from user where username = ?', [username]).fetchone()
    if chk is not None:
        return chk[0]
    else:
        return None

@app.before_request
def before_request():
    """Make sure we are connected to the database each request and look
    up the current user so that we know he's there.
    """
    g.db = connect_db()
    g.user = None
    if 'user_id' in session:
        g.user = query_db('select * from user where user_id = ?',
                          [session['user_id']], one=True)


@app.teardown_request
def teardown_request(exception):
    """Closes the database again at the end of the request."""
    if hasattr(g, 'db'):
        g.db.close()


@app.route('/')
def main():
    return render_template('home.html')

@app.route('/register', methods=['GET','POST'])
def register():
    if g.user:
        return redirect(url_for('home'))
    error=None
    if request.method == 'POST':
        if not request.form['id']:
            error='You have to enter a id'
        elif not request.form['nickname']:
            error='You have to enter a username'
        elif not request.form['email']:
            error='You have to enter a emali'
        elif '@' not in request.form['email']:
            error='You have to enter a valid email address'
        elif not request.form['password']:
            error='You have to enter a password'
        elif not request.form['password2']:
            error='You have to enter a password'
        elif request.form['password']!=request.form['password2']:
            error='Passwords not match'
        elif get_user_id(request.form['username']) is not None:
            error='The username is already taken'
        else:
            g.db.execute('insert into user(user_id, user_name, user_email, user_pw_hash) values(?, ?, ?, ?)',
                [request.form['id'], request.form['nickname'], request.form['email'], generate_password_hash(requset.form['password'])])
            g.db.commit()
            flash('You are successfully registered! you can login now')
            return redirect(url_for('login'))
    return render_template('register.html', error=error)

            
@app.route('/login', methods=['GET','POST'])
def login():
    if g.user:
        return redirect(url_for('home'))
    error=None
    if request.method == 'POST':
        user=g.db.execute('select * from user whrer username = ?', [request.form['username']])
        if user is None:
            error = 'Invalid username'
        elif not check_password_hash(user['pw_hash'], request.form['password']):
            error = 'Invalid password'
        else:
            flash('long in')
            session['user_id']=user['user_id']
            return redirect(url_for('home'))
    return render_template('login.html', error=error)

if __name__ == '__main__' :
    app.run()