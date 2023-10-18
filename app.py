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

# GET REQUESTS FOR LOG IN AND REGISTER

@app.route('/login', methods=['GET'])
def loginForm():
    return render_template('login.html')

@app.route('/register', methods=['GET'])
def registerForm():
    return render_template('register.html')

# POST REQUESTS FOR LOGIN AND REGISTER

@app.route('/login', methods=['POST'])
def processLogin():

    #Get the user data from form
    email = request.form['email']
    password = request.form['password']

    #TODO: Try to log user in by matching username and password
    getUser = db.users.find_one({'email': email})
    
    match = True
    if(getUser == None): 
        match = False
    
    if match == False: 

        # Fail user not found
        print("no documents found")

    elif(getUser["password"] != password): 
        
        # Fail passwords do not match
        print("Password Incorrect")

    else:
    #Success -> log the user in with their account & add COOKIE
        print("success")
        return render_template('events.html')

    return render_template('login.html')

@app.route('/register', methods=['POST'])
def processRegistration():

    #Get the user data from form
    email = request.form['email']
    username = request.form['username']
    password = request.form['password']
    confirmPassword = request.form['confirmPassword']


    #TODO: check for unique username/email? 

    #TODO: Check that passwords match -> if not route back to register with message
    
    #Create an account in the database
    newAccount = {
        'email' : email, 
        'username' : username, 
        'password' : password
    }

    db.users.insert_one(newAccount)
    
    #TODO: Log the user in with their created account & add COOKIE

    return render_template('register.html')


@app.route('/events', methods=['GET', 'POST'])
def event():
    if request.method == 'POST':
        search_query = request.form.get('search_query')
        search_option = request.form.get('search_option')
        query = {}
        if search_option == "event_name":
            query = {'eventName': {'$regex': search_query, '$options': 'i'}}
            docs = db['event'].find(query).sort("created_at", -1)
        elif search_option == "organizer":
            query = {'organizer': {'$regex': search_query, '$options': 'i'}}
        elif search_option == "description":
            query = {'description': {'$regex': search_query, '$options': 'i'}}
        elif search_option == "location":
            query = {'location': {'$regex': search_query, '$options': 'i'}}
        elif search_option == "date":
            query = {'date': {'$regex': search_query, '$options': 'i'}}
        docs = db['event'].find(query).sort("created_at", -1)
    else:
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



 
