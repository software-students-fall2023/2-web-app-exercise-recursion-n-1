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





