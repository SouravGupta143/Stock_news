from flask import Flask,render_template,request
import sqlite3 as sql
from urllib.request import urlopen
from bs4 import BeautifulSoup

app=Flask(__name__)

def connect(dbname):
    try:
        db=sql.connect(f"{dbname}.db")
        cur=db.cursor()
        return db,cur
    except Exception as e:
        print("Error" ,e)
        exit(2)

def fetchnews(dbname):
    db,cur=connect(dbname)
    if dbname=='indiainfoline':
        cur.execute('SELECT * FROM News ORDER BY id DESC LIMIT 1')
        lastrec=cur.fetchone()
        newslist=[]
        for var in range(1,3):
            url='https://www.indiainfoline.com/search/news/stocks/{0}'.format(var)
            data=urlopen(url)
            soup=BeautifulSoup(data,'lxml')
            li=soup.find_all('li',{'class':'animated'})
            for tag in li: 
                link='https://www.indiainfoline.com'+tag.find('a')['href']
                text=tag.find_all('p')
                text[0]=text[0].text.strip()
                text[1]=text[1].text.strip()
                if link==lastrec[3]:
                    break
                newslist.append([link,text])
            if link==lastrec[3]:
                break
                
        if len(newslist)!=0:        
                newslist=newslist[::-1]
                for val in newslist:
                    cur.execute("""INSERT INTO News(title,description,link)
                                VALUES(?,?,?)""",(val[1][0],val[1][1],val[0]))
                    db.commit()
        
    else:
        cur.execute('SELECT * FROM News ORDER BY id DESC LIMIT 1')
        lastrec=cur.fetchone()
        newslist=[]
        for var in range(1,3):
            url='https://www.cnbctv18.com/market/stocks/page-{0}/'.format(var)
            data=urlopen(url)
            soup=BeautifulSoup(data,'lxml')
            li=soup.find_all('div',{'class':'list_title'})
            for div in li: 
                link=div.find('a')['href']
                text=list(div.find('a').text.split('\n'))
                if text[0]==lastrec[1]:
                    break
                newslist.append((link,text))
            if text[0]==lastrec[1]:
                break
        if len(newslist)!=0:        
            newslist=newslist[::-1]

            for val in newslist:
                cur.execute("""INSERT INTO News(title,description,link)
                                VALUES(?,?,?)""",(val[1][0],val[1][1],val[0],))
                db.commit()
    db.close()
    return None


@app.route('/')
def index():
    for name in ['indiainfoline','cnbctv18']:
        fetchnews(name)
    db,cur=connect('indiainfoline')
    cur.execute("""SELECT * FROM (
   SELECT * FROM News ORDER BY id DESC LIMIT 5
    )Var1
   ORDER BY id ASC;""")
    news1=cur.fetchall()
    news1=news1[::-1]
    db.close()

    db,cur=connect('cnbctv18')
    cur.execute("""SELECT * FROM (
   SELECT * FROM News ORDER BY id DESC LIMIT 5
    )Var1
   ORDER BY id ASC;""")
    news2=cur.fetchall()
    news2=news2[::-1]
    db.close()
    return render_template('index.html',data1=enumerate(news1,start=1),data2=enumerate(news2,start=1))

@app.route('/cnbctv/')
def cnbctv18news():
    db,cur=connect('cnbctv18')
    cur.execute("SELECT * FROM News")
    news=cur.fetchall()
    news=news[::-1]
    db.close()
    return render_template('cnbctv18.html',data1=enumerate(news,start=1))

@app.route('/indiainfoline/')
def indiainfoline():
    db,cur=connect('indiainfoline')
    cur.execute("SELECT * FROM News")
    news=cur.fetchall()
    news=news[::-1]
    db.close()
    return render_template('indiainfoline.html',data1=enumerate(news,start=1))

@app.route('/part_iifl_news/', methods=['POST'])
def part_iifl_news():
    if request.method == 'POST':
        word=request.form['search']
        db,cur=connect('indiainfoline')
        cur.execute('Select * from News')
        news_list=cur.fetchall()
        word=word.lower()
        data=[]
        for news in news_list:
            if word in news[1].lower():
                data.append(news)
    db.close()
    return render_template("iifl_newser.html",data=enumerate(data,start=1))

@app.route('/part_cnbc_news/', methods=['POST'])
def part_cnbc_news():
    if request.method == 'POST':
        word=request.form['search']
        db,cur=connect('cnbctv18')
        cur.execute('Select * from News')
        news_list=cur.fetchall()
        word=word.lower()
        data=[]
        for news in news_list:
            if word in news[1].lower():
                data.append(news)
    db.close()
    return render_template("cnbc_newser.html",data=enumerate(data,start=1))


if __name__ == "__main__":  
    app.run(debug = True)  
