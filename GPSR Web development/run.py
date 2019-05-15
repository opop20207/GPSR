from flask import request, Flask, render_template
app = Flask(__name__)

@app.route('/')
def main():
    return render_template('home.html')

if __name__ == '__main__':
    app.run()