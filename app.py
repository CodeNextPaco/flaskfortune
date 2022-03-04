from flask import Flask, render_template, request
import requests
import sqlite3
from datetime import datetime


app = Flask(__name__)

def get_all_fortunes():
    print("getting all fortunes")
    #connect to DB
    conn = sqlite3.connect('./static/data/fortuneteller.db')
    curs = conn.cursor()
    all_fortunes = []
    rows = curs.execute("SELECT * from fortunes")
    for row in rows:
        fortune = {'fortune': row[0],  'date': row[1]}
        all_fortunes.append(fortune)
    conn.close()

    return all_fortunes



def store_fortune(new_fortune, fortune_date):

    print("Storing new Fortune!")


    #connect to database
    conn = sqlite3.connect('./static/data/fortuneteller.db')
    curs = conn.cursor()

    curs.execute("INSERT INTO fortunes (fortune, date) VALUES((?),(?))",(new_fortune, fortune_date ))
    conn.commit()
    #close database connection
    conn.close()



@app.route('/')
def index():
    return render_template('index.html')

@app.route('/login', methods=["POST"])
def login():
    print("Logging in...")
    data = {
        "message": "Welcome!",

    }
    return render_template('index.html', data=data)

@app.route('/admin')
def home():

    fortunes = get_all_fortunes()



    if len(fortunes) > 0:
        print("We have fortunes to pass on!")

        data = {
            "all_fortunes": fortunes
        }

        return render_template('admin.html', data=data)

       

    return render_template('admin.html')
        
    
    


@app.route('/post_fortune', methods=['POST'])
def post_fortune():

    print("posting fortune: ")
    fortune = request.form["fortune-input"]
    now = datetime.now() # current date and time   

    date_time = now.strftime("%m/%d/%Y, %H:%M:%S")
    print("date and time:",date_time)

    #Store the message in the DB
    store_fortune(fortune, date_time)

    fortunes = get_all_fortunes()
    if len(fortunes) > 0:
        data = {

            "all_fortunes": fortunes
        }

        return render_template('admin.html',data=data )

    return render_template('admin.html' )

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0')