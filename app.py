from this import d
from flask import Flask, render_template, request
import sqlite3
from datetime import datetime
import random

app = Flask(__name__)

def get_random_fortune():

    #returns a random fortune
    
    all_fortunes = get_all_fortunes() # returns a list by our own function
    random_choice = random.choice(all_fortunes) # import random to use this
    random_fortune = random_choice["fortune"]
    print(random_fortune)
    
    return random_fortune

    

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

def get_all_users():
    print("getting all users...")

     #connect to DB
    conn = sqlite3.connect('./static/data/fortuneteller.db')
    curs = conn.cursor()
    all_users = []
    rows = curs.execute("SELECT * from users")
    for row in rows:
        user = {'name': row[0],  'username': row[1]}
        all_users.append(user)
    conn.close()

    return all_users


def store_fortune(new_fortune, fortune_date):

    print("Storing new Fortune!")

    #connect to database
    conn = sqlite3.connect('./static/data/fortuneteller.db')
    curs = conn.cursor()
    #insert a new row to the db and commit
    curs.execute("INSERT INTO fortunes (fortune, date) VALUES((?),(?))",(new_fortune, fortune_date ))
    conn.commit()
    #close database connection
    conn.close()



@app.route('/')
def index():
    print("index.html")
    
    random_fortune = get_random_fortune()

    data = {
        "random_fortune": random_fortune
    }
    print(random_fortune)

    return render_template('index.html', data=data)

@app.route('/login', methods=["POST"])
def login():
    print("Logging in...")

    data = {
        "message": "Welcome!",

    }
    return render_template('index.html', data=data)

@app.route('/admin')
def admin_home():

    fortunes = get_all_fortunes()
    users = get_all_users()
    
   
    if len(fortunes) > 0:
        print("We have fortunes to pass on!")

        data = {
            "all_fortunes": fortunes,
            "all_users": users
        }

    return render_template('admin.html', data=data)

       

    
        
    
    


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