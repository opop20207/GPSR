from __future__ import with_statement
import time
from sqlite3 import dbapi2 as sqlite3
from hashlib import md5
from datetime import datetime
from contextlib import closing
from flask import Flask, request, session, url_for, redirect, \
     render_template, abort, g, flash
from werkzeug.security import check_password_hash, generate_password_hash
import os
#settings
app = Flask(__name__)
app.config.from_pyfile('config.py')

######################################################################################################################################################
#######################################################################################################################################################
#base function

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
#######################################################################################################################################################
#######################################################################################################################################################
#before, teardown function

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

#######################################################################################################################################################
#######################################################################################################################################################
#home
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

#######################################################################################################################################################
#######################################################################################################################################################
#group

@app.route('/group',methods=['GET','POST'])
def group():
    return render_template('group.html')

#######################################################################################################################################################
#######################################################################################################################################################
#problem

@app.route('/problem',methods=['GET','POST'])
def problem():
    if not g.user:
        return redirect(url_for('home'))
    problem_list=query_db('select * from problem')
    return render_template('/problem/problem.html', problem_list=problem_list)
    
@app.route('/problem/<problem_num>', methods=['GET', 'POST'])
def problem_view(problem_num):
    problem = query_db('select * from problem where problem_num is ?', [problem_num])
    return render_template('/problem/problem_view.html', problem=problem)

@app.route('/problem/<problem_num>/view_io')
def problem_view_io(problem_num):
    return "hi"

@app.route('/problem/compile', methods=['GET', 'POST'])
def problem_compile():
    a={'answer_problem_num':request.form['answer_problem_num'],
       'answer_language':request.form['language'],
       'answer_who':g.user['user_id'],
       'answer_text':request.form['answer_text'],
       'answer_result':0}
    
    if a['answer_language'] == 'C':
        res = problem_compile_C(a)
    elif a['answer_language'] == 'C++':
        res = problem_compile_Cpp(a)
    elif a['answer_language'] == 'Java':
        res = problem_compile_Java(a)
    elif a['answer_language']=='Python':
        res = problem_compile_Python(a)
        
    if res==0:
        error="compile error!"
    elif res==1:
        error="Wrong!"
    elif res==2:
        error="Success!"
    
    a['answer_result']=res
    g.db.execute('insert into answer(answer_problem_num, answer_language,answer_who,answer_text,answer_result) values(?,?,?,?,?)',
                 [a['answer_problem_num'],a['answer_language'],a['answer_who'],a['answer_text'],res])
    g.db.commit()
    return render_template('/problem/problem_result.html', error=error, a=a)

def problem_compile_C(a):
    file=open('test_file.c', 'w')
    file.write(a['answer_text'])
    file.close()
    
    command_inputfile = 'io/'+str(a['answer_problem_num'])+'/'+str(a['answer_problem_num'])+'.in'    
    command_outputfile = 'io/'+str(a['answer_problem_num'])+'/'+str(a['answer_problem_num'])+'.out'
    
    f = os.system('gcc test_file.c')
    if f == 0:
        temp1 = os.popen('a.exe < '+command_inputfile, "r").read()
        temp2 = open(command_outputfile, "r").read()
        print(temp1)
        print(temp2)
        os.remove('a.exe')
        if temp1 == temp2:
            res=2
        else:
            res=1
    else:
        res=0
    os.remove('test_file.c')
    
    return res

def problem_compile_Cpp(a):
    file=open('test_file.cpp', 'w')
    file.write(a['answer_text'])
    file.close()
    
    command_inputfile = 'io/'+str(a['answer_problem_num'])+'/'+str(a['answer_problem_num'])+'.in'    
    command_outputfile = 'io/'+str(a['answer_problem_num'])+'/'+str(a['answer_problem_num'])+'.out'
    
    f = os.system('g++ test_file.cpp')
    if f == 0:
        temp1 = os.popen('a.exe < '+command_inputfile, "r").read()
        temp2 = open(command_outputfile, "r").read()
        print(temp1)
        print(temp2)
        os.remove('a.exe')
        if temp1 == temp2:
            res=2
        else:
            res=1
    else:
        res=0
    os.remove('test_file.cpp')
    
    return res

def problem_compile_Java(a):
    file=open('test_file.java', 'w')
    file.write(a['answer_text'])
    file.close()
    
    command_inputfile = 'io/'+str(a['answer_problem_num'])+'/'+str(a['answer_problem_num'])+'.in'    
    command_outputfile = 'io/'+str(a['answer_problem_num'])+'/'+str(a['answer_problem_num'])+'.out'
    
    f = os.system('javac test_file.java')
    if f == 0:
        temp1 = os.popen('java Main < '+command_inputfile, "r").read()
        temp2 = open(command_outputfile, "r").read()
        print(temp1)
        print(temp2)
        if temp1 == temp2:
            res=2
        else:
            res=1
        os.remove('Main.class')
    else:
        res=0
    os.remove('test_file.java')
    
    return res

def problem_compile_Python(a):
    file=open('test_file.py', 'w')
    file.write(a['answer_text'])
    file.close()
    
    command_inputfile = 'io/'+str(a['answer_problem_num'])+'/'+str(a['answer_problem_num'])+'.in'    
    command_outputfile = 'io/'+str(a['answer_problem_num'])+'/'+str(a['answer_problem_num'])+'.out'
    
    f = os.system('python -m py_compile test_file.py')
    if f == 0:
        temp1 = os.popen('python test_file.py < '+command_inputfile, "r").read()
        temp2 = open(command_outputfile, "r").read()
        print(temp1)
        print(temp2)
        if temp1 == temp2:
            res=2
        else:
            res=1
    else:
        res=0
    os.remove('test_file.py')
    
    return res

#######################################################################################################################################################
#######################################################################################################################################################
#talk

@app.route('/talk',methods=['GET','POST'])
def talk():
    if not g.user:
        return redirect(url_for('home'))
    talk_list=query_db('select * from board')
    return render_template('/talk/talk.html', talk_list=talk_list)

@app.route('/talk/<board_num>', methods=['GET','POST'])
def talk_view(board_num):
    talk = query_db('select * from board where board_num is ?', [board_num])
    return render_template('/talk/talk_view.html',talk=talk, who_id=g.user['user_id'])

@app.route('/talk/write')
def talk_write():
    return render_template('/talk/talk_write.html')

@app.route('/talk/add',methods=['GET','POST'])
def talk_add():
    error=None
    if request.method == 'POST':
        if not request.form['talk_title']:
            error="You have to enter a title"
        elif not request.form['talk_body']:
            error="You have to enter a body"
        else:
            g.db.execute('insert into board (board_name, board_text, board_who) values (?, ?, ?)',
                         [request.form['talk_title'],request.form['talk_body'],g.user['user_id']])
            g.db.commit()
            return redirect(url_for('talk'))
    return render_template('/talk/talk_write.html', error=error)

@app.route('/talk/delete/<board_num>',methods=['POST','GET'])
def talk_delete(board_num):
    g.db.execute('delete from board where board_num = ?', board_num)
    g.db.commit()
    return redirect(url_for('talk'))

#######################################################################################################################################################
#######################################################################################################################################################
#admin

@app.route('/geonguprincesssecretroom')
def admin():
    return render_template('/admin/admin.html')

#view user_list
@app.route('/geonguprincesssecretroom/view_user')
def admin_view_user():
    return render_template('/admin/admin_view_user.html',users=query_db('''
    select * from user limit?''', [PER_PAGE]))
    
@app.route('/geonguprincesssecretroom/view_problem')
def admin_view_problem():
    return render_template('/admin/admin_view_problem.html',problems=query_db('''
    select * from problem limit?''', [PER_PAGE]))

#all of user information
@app.route('/geonguprincesssecretroom/view_user_info/<user_id>')
def admin_view_user_info(user_id):
    user = query_db('select * from user where user_id = ?', [user_id], True)
    return render_template('/admin/admin_view_user_info.html', user=user)

#user delete
@app.route('/geonguprincesssecretroom/delete_user/<user_id>')
def admin_delete_user(user_id):
    g.db.execute('delete from user where user_id = ?', [user_id])
    g.db.commit()
    return redirect(url_for('admin_view_user'))

@app.route('/geonguprincesssecretroom/add_problem')
def admin_add_problem():
    return render_template('/admin/admin_add_problem.html', error=None)

@app.route('/geonguprincesssecretroom/add_problem_exe',methods=['POST'])
def admin_add_problem_exe():
    error=None
    if request.method == 'POST':
        if not request.form['problem_name']:
            error="You have to enter a name"
        elif not request.form['problem_text_info']:
            error="You have to enter a text_info"
        elif not request.form['problem_text_input_info']:
            error="You have to enter a text_input_info"
        elif not request.form['problem_text_output_info']:
            error="You have to enter a text_output_info"
        else:
            g.db.execute('insert into problem(problem_name,problem_correct,problem_text_info,problem_text_input_info,problem_text_output_info) values(?, ?, ?, ?, ?)',
                         [request.form['problem_name'], 0, request.form['problem_text_info'],request.form['problem_text_input_info'],request.form['problem_text_output_info']])
            g.db.commit()
            return redirect(url_for('admin_view_problem'))
    return render_template('/admin/admin_add_problem.html', error=error)

@app.route('/geonguprincesssecretroom/delete_problem/<problem_num>')
def admin_delete_problem(problem_num):
    g.db.execute('delete from problem where problem_num = ?', [problem_num])
    g.db.commit()
    return redirect(url_for('admin_view_problem'))

@app.route('/geonguprincesssecretroom/view_problem_info/<problem_num>')
def admin_view_problem_info(problem_num):
    problem = query_db('select * from problem where problem_num = ?', [problem_num], True)
    return render_template('/admin/admin_view_problem_info.html', problem=problem)

#######################################################################################################################################################
#######################################################################################################################################################

if __name__ == '__main__' :
    init_db()
    app.run()