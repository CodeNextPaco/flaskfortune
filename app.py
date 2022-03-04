from flask import Flask, render_template, request
import sqlite3
from datetime import datetime


app = Flask(__name__)




def get_all_fortunes():

    #connect to DB
 
    all_fortunes = []


    return all_fortunes



def store_fortune(new_fortune, fortune_date):

    print("Storing new Fortune!")

    #connect to database

    #insert a new row to the db and commit
    
    #close database connection
  



@app.route('/')
def index():


    return render_template('index.html')

  

@app.route('/admin')
def admin_home():

    #get all fortunes
    fortunes = get_all_fortunes() 
     
    #call get_all_users


    #pass on your fortunes and users to your client
    data = {}

    return render_template('admin.html', data=data)

       

    


@app.route('/post_fortune', methods=['POST'])
def post_fortune():

    print("posting fortune: ")
    #get the fortune text from fortune-input
    fortune = request.form["fortune-input"]
    now = datetime.now() # current date and time   

    date_time = now.strftime("%m/%d/%Y, %H:%M:%S")
    print("date and time:",date_time)

    #Store the message in the DB
    store_fortune(fortune, date_time)

    data ={}
    fortunes = get_all_fortunes()
    #if there are fortunes, store them in the dictionary
    if len(fortunes) > 0:
        data = {

            "all_fortunes": fortunes
        }

        

    return render_template('admin.html',data=data )

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0')