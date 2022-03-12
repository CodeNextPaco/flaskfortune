from flask import Flask, render_template, request, redirect, url_for, session
# The Session instance is not used for direct access, you should always use flask.session
from flask_session import Session
import sqlite3
from datetime import datetime
import random
from twilio.rest import Client

import idna


app = Flask(__name__)
app.config["SESSION_PERMANENT"] = False #allow it to expire
app.config["SESSION_TYPE"] = "filesystem" #store the session locally
Session(app)



########################### DATABASE FUNCTIONS #############################

def update_fortune(rowid, fortune):

    conn = sqlite3.connect('./static/data/fortuneteller.db')
    curs = conn.cursor()
    result  = curs.execute("UPDATE fortunes SET fortune=(?) WHERE rowid=(?)", [fortune, rowid])
    conn.commit()
    #close database connection
    conn.close()

def get_fortune_by_id(rowid):

    fortune = {}
    conn = sqlite3.connect('./static/data/fortuneteller.db')
    curs = conn.cursor()
    result  = curs.execute("SELECT rowid, * FROM fortunes WHERE rowid=(?)", [rowid])
    

    #You can instead use cursor.fetchall()[0] to get the first item returned by your query.
    for row in result:
        fortune = {'id': row[0],  'fortune': row[1]}
    
    conn.close()
    return fortune

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
    result  = curs.execute("SELECT name, username, password FROM users WHERE username=(?) AND password= (?)", [username, password])
  
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
    
    #this function uses the row id to search for the one to delete in the db.
    if table=="fortunes":

        curs.execute("DELETE FROM fortunes WHERE rowid=(?)", (id,))
        print("Deleting fortune id : " + id)
        conn.commit()
         

    elif table=="users":
        curs.execute("DELETE FROM user WHERE rowid=(?)", (id,))
        print("Deleting user id : " + id)
        conn.commit()
         
  
    #close database connection
    conn.close()

    
     

################################ PAGE ROUTES ##################################

@app.route('/')
def index():

    if session["name"]:
        return redirect(url_for('user_home'))

    return render_template('index.html')

@app.route("/home")
def user_home():
    print("were home!")

    data ={}

    #check the session to see if there is a user logged in
    if session.get("name"):

        return render_template('home.html' , data=data)

    else:
        return redirect(url_for('index'))
        

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

    username = request.form["username-field"]
    password = request.form["password-field"]

    data = {}
    user = validate_user(username, password)

    if user:
        #save the user into the session so it remembers them
        session["name"] = user["name"]

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
    
@app.route('/logout')
def logout():
    session["name"] = None
    return redirect(url_for('index'))


@app.route("/get_fortune", methods=["GET"])
def get_fortune():
    print("getting fortune")

    fortune = get_random_fortune()

    data = {

        "fortune" : fortune
    }

    return render_template('home.html', data=data)

    
@app.route('/delete-fortune/<id>')
def delete_fortunte(id):
    print("deleting fortune: " + id)

    #this should return an updated list, minus the one we deleted.
    delete_row("fortunes", id)
 
    return redirect(url_for('admin_home') )


@app.route('/admin/post_fortune', methods=['POST'])
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
 
      #  return render_template('admin.html',data=data )
    return redirect(url_for('admin_home'))
    #return render_template('admin.html' )


@app.route('/edit-fortune/<id>', methods=["POST", "GET"])
def edit_fortune(id ):

    #if the edit is made, then we handle it as POST request
    if request.method == 'POST':
        updated_fortune = request.form['fortune-edit-input']

        update_fortune(id, updated_fortune) #updates the fortune
        return redirect(url_for('admin_home'))
 
    print("edit fortune #" + id)

    data ={}

    fortune = get_fortune_by_id(id)

    print(fortune)

    if fortune:
        data={
            "fortune": fortune
            }

    return render_template('edit.html' , data=data)


############################### Twilio ##################################    


@app.route('/send_sms' , methods=["POST"])
def send_sms():

    print("Sending message")
    recipient_number = request.form["tel-input"]
    fortune_to_send = request.form["fortune-sms"]
    print(fortune_to_send)
     
    prefix = "+1"
    #print(number)

    #Adding a simple message
    sms_body = fortune_to_send
    number = prefix+recipient_number

    #read about securing tokens in environment variables:
    # https://www.twilio.com/docs/usage/secure-credentials
  
     

    twilio_acct_id = 'AC7dc9522a056142318ab0305ae59473dc'
    twilio_phone_number = '+14143124358'
    twilio_auth_token = '9722c766f2f769c3718e86b0236ba5c0'


    client = Client(twilio_acct_id, twilio_auth_token)

    message = client.messages.create(
        to= number, 
        from_= twilio_phone_number,
        body= sms_body)

    print(f"Message id:  {message.sid}")
  
    return redirect(url_for("user_home"))


if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0')