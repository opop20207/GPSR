from flask import request, Flask, render_template
app = Flask(__name__)

@app.route('/')
def main():
    return render_template('home.html')

@app.route('/<number>')
def numb(number):
    return number

@app.route('/info', methods=['POST'])
def info():
    error=None
    myage=request.form['age']
    return render_template('info.html', age=myage)
