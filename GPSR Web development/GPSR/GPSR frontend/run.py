from flask import request, Flask, render_template
app = Flask(__name__)

@app.route('/')
def main():
    return render_template('home.html')

@app.route('/group')
def group():
    return render_template('group.html')

@app.route('/info', methods=['POST', 'GET'])
def info():
    if request.method == 'POST':
        return render_template('info.html')
    else:
        return render_template('info.html')
    
if __name__ == '__main__':
    app.run()