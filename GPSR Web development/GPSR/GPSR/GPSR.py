from __future__ import with_statement
import time
from sqlite3 import dbapi2 as sqlite3
from hashlib import md5
from datetime import datetime
from contextlib import closing
from flask import Flask, request, session, url_for, redirect, \
     render_template, abort, g, flash
from werkzeug.security import check_password_hash, generate_password_hash

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
            db.cursor().executescript(f.read())
        db.commit()
        

def query_db(query, args=(), one=False):
    cur = g.db.execute(query, args)
    rv = [dict((cur.description[idx][0], value)
               for idx, value in enumerate(row)) for row in cur.fetchall()]
    return (rv[0] if rv else None) if one else rv

        
def get_user_num(id):
    chk = g.db.execute('select user_num from user where user_id = ?', [id]).fetchone()
    if chk is not None:
        return chk[0]
    else:
        return None

@app.before_request
def before_request():
    g.db = connect_db()
    g.user = None
    if 'user_num' in session:
        g.user = query_db('select * from user where user_num = ?',
                          [session['user_num']], one=True)


@app.teardown_request
def teardown_request(exception):
    if hasattr(g, 'db'):
        g.db.close()


@app.route('/')
def home():
    uiid=None
    uinickname=None
    if g.user:
        return render_template('home.html',user_info_id=g.user['user_id'], user_info_nickname=g.user['user_nickname'])
    return render_template('home.html', user_info_id=uiid, user_info_nickname=uinickname)

@app.route('/register', methods=['GET','POST'])
def register():
    if g.user:
        return redirect(url_for('home'))
    error=None
    if request.method == 'POST':
        if not request.form['id']:
            error='You have to enter a id'
        elif not request.form['nickname']:
            error='You have to enter a nickname'
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
        elif get_user_num(request.form['id']) is not None:
            error='The id is already taken'
        else:
            g.db.execute('insert into user(user_id, user_nickname, user_email, user_pw_hash) values(?, ?, ?, ?)',
                [request.form['id'], request.form['nickname'], request.form['email'], generate_password_hash(request.form['password'])])
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
        user=query_db('select * from user where user_id = ?', [request.form['id']], one=True)
        if user is None:
            error = 'Invalid username'
        elif not check_password_hash(user['user_pw_hash'], 
                                     request.form['password']):
            error = 'Invalid password'
        else:
            flash('log in')
            session['user_num']=user['user_num']
            return redirect(url_for('home'))
    return render_template('login.html', error=error)

@app.route('/logout')
def logout():
    session.pop('user_num', None)
    return redirect(url_for('home'))

@app.route('/geonguprincesssecretroom')
def admin():
    return render_template('/admin/admin.html')
    
#view user_list
@app.route('/geonguprincesssecretroom/view_user')
def admin_view_user():
    return render_template('/admin/admin_view_user.html',users=query_db('''
    select * from user limit?''', [PER_PAGE]))

#user delete
@app.route('/geonguprincesssecretroom/delete_user/<user_id>')
def admin_delete_user(user_id):
    g.db.execute('delete from user where user_id = ?', [user_id])
    g.db.commit()
    return redirect(url_for('/admin/admin_view_user',user_id=user_id))
        
#all of information of user
@app.route('/geonguprincesssecretroom/view_all/<user>')
def view_all(user):
    return render_template('/admin/admin_view_all.html',user=user.split(','))

@app.route('/geonguprincesssecretroom/add_problem')
def admin_add_problem():
    return 'hi'


if __name__ == '__main__' :
    init_db()
    app.run()