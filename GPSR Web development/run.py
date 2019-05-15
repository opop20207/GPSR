from flask import request, Flask, render_template
from sqlite3 import dbapi2 as sqlite3
app = Flask(__name__)
app.config.from_object(__name__)

Debug=True

@app.route('/')
def main():
    return render_template('home.html')

if __name__ == '__main__':
    app.run()