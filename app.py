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
def show_profile(): # TODO : NEED TO RETRIEVE CURRENT USER FROM SESSION

    user = db.users.find_one({"_id": ObjectId("652eb539c801041c945081fc")})
    
    return render_template('profile.html', user=user)
   
























