from flask import Flask, render_template, request, redirect, abort, url_for, make_response
import pymongo
from bson.objectid import ObjectId
from pymongo import MongoClient
import os
import dotenv
from dotenv import load_dotenv
from db import db

app = Flask(__name__)

if ( os.getenv('FLASK_ENV','development') == 'development'):
    app.debug = True

@app.route('/')
def home():
    return render_template('index.html', content="Greetings!")

@app.route('/login', methods=['POST'])
def login():
    return render_template('login.html')

@app.route('/register', methods=['POST'])
def register():
    return render_template('register.html')

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

if __name__ == "__main__":
    PORT = os.getenv('PORT', 8000)
    app.run(host='0.0.0.0', port=PORT)



 