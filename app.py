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

    #Try to log the user in

    #Success -> log the user in with their account

    #Fail -> forward the user to back to the log in page & notify of failure

    return render_template('login.html')

@app.route('/register', methods=['POST'])
def processRegistration():

    #Get the user data from form
    email = request.form['email']
    username = request.form['username']
    password = request.form['password']
    confirmPassword = request.form['confirmPassword']


    #Create an account in the database

    #Log the user in with their created account

    return render_template('register.html')

