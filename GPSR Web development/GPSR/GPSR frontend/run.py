from flask import request, Flask, render_template
app = Flask(__name__)

@app.route('/')
def main():
    return render_template('home.html')

@app.route('/problem')
def problem():
    return render_template('problem.html')

@app.route('/info', methods=['POST', 'GET'])
def info():
    if request.method == 'POST':
        mynickname=request.form['nickname']
        mypassword=request.form['password']
        return render_template('info.html', nickname=mynickname, password=mypassword)
    else:
        mynickname = request.args.get('nickname')
        mypassword = request.args.get('password')
        return render_template('info.html', nickname=mynickname, password=mypassword)
    
if __name__ == '__main__':
    app.run()