from flask import Flask, render_template, request, redirect, abort, url_for, make_response
import pymongo
from bson.objectid import ObjectId
from pymongo import MongoClient
import os
import dotenv
from dotenv import load_dotenv
from db import db
import datetime
from bson.dbref import DBRef


app = Flask(__name__)

if ( os.getenv('FLASK_ENV','development') == 'development'):
    app.debug = True

@app.route('/')
def home():
    return render_template('index.html', content="Greetings!")

@app.route('/login', methods=['POST','GET'])
def login():
    return render_template('login.html')

@app.route('/register', methods=['POST','GET'])
def register():
    return render_template('register.html')


@app.route('/profile')
def show_profile(): 

    user = db.users.find_one({"_id": ObjectId('652f7b647ceddb5eeac63b77')}) # TODO : NEED TO RETRIEVE CURRENT USER FROM SESSION
  
    #myEvts = db.event.find_one({"_id": ObjectId("652f5cb3e3782d2a799feb73")}) #temp data 
    #myPosting = db.event.find({}) #temp data

    for event in user['myEvents']:
        event_id = event['id']
        event_details = db.event.find_one({"_id": ObjectId(event_id)})
        event.update(event_details)
  

    
    return render_template('profile.html', user=user)



@app.route('/events', methods=['GET', 'POST'])
def event():
    docs = db['event'].find({}).sort("created_at", -1)
    return render_template('events.html', docs=docs)
    

@app.route('/add_event', methods=['GET', 'POST'])
def add_event():
     if request.method == 'POST':
        event_name = request.form.get('eventName')
        organizer = request.form.get('organizer')
        date = request.form.get('date')
        time = request.form.get('time')
        point_of_contact = request.form.get('pointOfContact')
        location = request.form.get('location')
        description = request.form.get('description')
        num_of_ppl = request.form.get('numOfPpl')

        new_event = {
            "eventName": event_name,
            "organizer": organizer,
            "date": date,
            "time": time,
            "pointOfContact": point_of_contact,
            "location": location,
            "description": description,
            "numOfPpl": num_of_ppl,
        }
        db['event'].insert_one(new_event)
        return redirect(url_for('event'))
     
     return render_template('add_event.html')



#TO BE DELETED AFTER !! THIS IS FOR THE PURPOSE OF CREATING USER DATA
#SOME  DATA HERE IS HARD CODED
@app.route('/add_user',methods=['POST'])
def createUser():
   

    doc = {
        "name" : "sky1",
        "email" : "sky1@gmail.com",
        "password" : "1234",
        "myEvents": [
            {"id": ObjectId("652f5ec73c5916795f01da0f")},
            {"id": ObjectId('652f5cb3e3782d2a799feb73')}
        ],       "myPostings":[]
       
    }

    db.users.insert_one(doc)

    return doc




if __name__ == "__main__":
    PORT = os.getenv('PORT', 8000)
    app.run(host='0.0.0.0', port=PORT)




 