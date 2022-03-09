from flask import Flask, render_template, request
import sqlite3
from datetime import datetime
import random

import idna


app = Flask(__name__)

########################### DATABASE FUNCTIONS #############################
def get_random_fortune():

    #returns a random fortune
    
    all_fortunes = get_all_fortunes() # returns a list by our own function
    random_choice = random.choice(all_fortunes) # import random to use this
    random_fortune = random_choice["fortune"]
    print(random_fortune)
    
    return random_fortune

def validate_user(username, password):
    print("validating user...")
    user = {}

    conn = sqlite3.connect('./static/data/fortuneteller.db')
    curs = conn.cursor()
    #get all columns if there is a match
    result  = curs.execute("SELECT rowid, name, username, password FROM users WHERE username=(?) AND password= (?)", [username, password])
  
    for row in result:
       user = {'name': row[0],  'username': row[1]}
         
    conn.close()
    return user

def get_all_fortunes():
    print("getting all fortunes")
    #connect to DB
    conn = sqlite3.connect('./static/data/fortuneteller.db')
    curs = conn.cursor()
    all_fortunes = []

    #all sql rows have a row id by default. use that to reference each one.
    rows = curs.execute("SELECT rowid, * from fortunes")
    for row in rows:
        fortune = {'rowid': row[0], 'fortune': row[1],  'date': row[2]}
        all_fortunes.append(fortune)
        print(fortune)
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

def delete_row(table, id):
    conn = sqlite3.connect('./static/data/fortuneteller.db')
    curs = conn.cursor()
    updated_rows=[]
    #this function uses the row id to search for the one to delete in the db.
    if table=="fortunes":

        curs.execute("DELETE FROM fortunes WHERE rowid=(?)", (id,))
        print("Deleting fortune id : " + id)
        updated_rows = get_all_fortunes()

    elif table=="users":
        curs.execute("DELETE FROM user WHERE rowid=(?)", (id,))
        print("Deleting user id : " + id)
        updated_rows = get_all_users()

    conn.commit()
    #close database connection
    conn.close()

    

    return updated_rows

################################ PAGE ROUTES ##################################

@app.route('/')
def index():
    return render_template('index.html')

@app.route("/home")
def user_home():
    print("were home!")

    return render_template('home.html')


@app.route('/admin/')
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

    return render_template('admin.html')

############################### GET/POST ##################################    

@app.route('/login', methods=["POST"])
def login():
    print("Logging in...")

    username = request.form["username-field"]
    password = request.form["password-field"]

    data = {}
    user = validate_user(username, password)

    if user:
        success_msg = "Welcome, "+ user["name"]

        data = {
            "name": user["name"],
            "username": user["username"]
        }

        #load home if there is a user, along with data.
        return render_template('home.html', data=data)

    else: 
        error_msg = "Login failed"

        data = {
            "error_msg": error_msg
        }
        #no user redirects back to the main login page, with error msg.
        return render_template('index.html', data=data)
    
@app.route("/get_fortune", methods=["GET"])
def get_fortune():
    print("getting fortune")

    fortune = get_random_fortune()

    data = {

        "fortune" : fortune
    }

    return render_template('home.html', data=data)

@app.route('/edit-fortune/<id>')
def edit_fortune():

    data={}
    return render_template('admin.html', data=data)
    
@app.route('/delete-fortune/<id>')
def delete_fortunte(id):
    print("deleting fortune: " + id)

    
    #get_all_fortunes should return an updated list.

    fortunes = delete_row("fortunes", id)
    users = get_all_users()

    data={
         "all_fortunes": fortunes,
         "all_users": users

    }

    return render_template('admin.html',data=data )


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