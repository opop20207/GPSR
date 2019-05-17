from flask import Flask,render_template,request, url_for, redirect
from bs4 import BeautifulSoup
import requests
app = Flask(__name__)

@app.route('/')
def home():
    lst = []
    url = "https://en.wikipedia.org/wiki/Turing_Award"
    res = requests.get(url)
    
    soup=BeautifulSoup(res.content,'html.parser')
    
    page=soup.find('table',class_='wikitable')
   
    for i in page.find_all('tr'):
        year=i.find('th')
        name=i.find('td')
        if name is None:
            continue
        name=name.find('a')
        if year is None:
            lst.append(name.get_text())
            continue
        lst.append('gg')
        lst.append(year.get_text())
        lst.append(name.get_text())
    
    return render_template('home.html', lst=lst)

if __name__ == '__main__':
    app.run()
    