from flask import Flask,render_template
app=Flask(__name__)

@app.route('/')
def home():
    return 'hi'

@app.route('/sd')
def home1():
    return render_template('home.html')

@app.route('/gg')
def g():
    return 'gg'

@app.route('/gg/<name>')
def n(name):
    return str(eval(name + "*" + name))

if __name__=='__main__':
    app.run()