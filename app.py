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
    getUser = db.users.find_one({'email': "testing"})
    
    match = True;
    if(getUser == None): 
        match = False
    

    if match == false: 

        # Fail user not found
        print("no documents found")

    elif(getUser.password != password): 
        
        # Fail passwords do not match
        print("no documents found")

    else:
    #Success -> log the user in with their account & add COOKIE
        print("success")

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
