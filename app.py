from flask import Flask, render_template, request, redirect, abort, url_for, make_response
import pymongo
from bson.objectid import ObjectId
from pymongo import MongoClient

from db import db

app = Flask(__name__)

@app.route('/')
def home():
    return render_template('index.html', content="Hello World!")