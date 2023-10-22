from flask import (
    Flask,
    render_template,
    request,
    redirect,
    abort,
    url_for,
    make_response,
    session
)
import pymongo
from bson.objectid import ObjectId
from pymongo import MongoClient
import os
import dotenv
from dotenv import load_dotenv
from db import db
import sys

app = Flask(__name__)
app.secret_key = os.urandom(24)

if os.getenv("FLASK_ENV", "development") == "development":
    app.debug = True

@app.route("/")
def loading():
    return render_template("index.html", content="Greetings!")

# GET REQUESTS FOR LOG IN AND REGISTER

@app.route("/login", methods=["GET"])
def loginForm():
     #Check if user has just tried to log in and failed vis a vis a passed variable
    incorrect_login = request.args.get('incorrect_login', False)

    return render_template("login.html", incorrect_login=incorrect_login)

@app.route("/register", methods=["GET"])
def registerForm():
    noPasswordMatch = request.args.get('noPasswordMatch', False)
    userExists = request.args.get('userExists', False)

    return render_template("register.html", noPasswordMatch = noPasswordMatch, userExists=userExists )


# POST REQUESTS FOR LOGIN AND REGISTER

@app.route("/login", methods=["POST"])
def processLogin():
    # Get the user enterd form data
    email = request.form["email"]
    password = request.form["password"]

    #Try to match the user entered email with a document in the database
    getUser = db.users.find_one({"email": email})

    match = True
    if getUser == None:
        match = False

    # Fail user not found
    if match == False:
        print("no matching user document found")
        return render_template("login.html", incorrect_login=True)

    # Fail passwords do not match
    elif getUser["password"] != password:
        print("Password Incorrect")
        return render_template("login.html", incorrect_login=True)
    
    # Success -> log the user in with their account & add COOKIE
    else:
        print("hello session")
        session['userid'] = str(getUser["_id"])
        session['email'] = email
        print(session)
        # print(session.get('email', "example@example.com")) 

        return redirect(url_for("event"))


@app.route("/register", methods=["POST"])
def processRegistration():
    # Get the user data from form
    email = request.form["email"]
    username = request.form["name"]
    password = request.form["password"]
    confirmPassword = request.form["confirmPassword"]

    #check the user ented email is unique -> If not route back to register page with message
    getUser = db.users.find_one({"email": email})

    match = True
    if getUser == None:
        match = False

    if(match): 
        return render_template("register.html", userExists=True)

    #Check that passwords match -> if not route back to register page with message
    if(password != confirmPassword): 
         return render_template("register.html", noPasswordMatch=True)

    # Create an account in the database
    newAccount = {"email": email, "name": username, "password": password,"myEvents":[],"myPostings":[]}
    db.users.insert_one(newAccount)

    #Success -> orward user to the log in page
    return render_template("login.html")


@app.route("/events", methods=["GET", "POST"])
def event():

    #example of pulling email from the session, example@example.com is the default if no email is found
    print(session.get('email', "example@example.com")) 

    if request.method == "POST":
        search_query = request.form.get("search_query")
        search_option = request.form.get("search_option")
        query = {}
        if search_option == "event_name":
            query = {"eventName": {"$regex": search_query, "$options": "i"}}
            docs = db["event"].find(query).sort("created_at", -1)
        elif search_option == "organizer":
            query = {"organizer": {"$regex": search_query, "$options": "i"}}
        elif search_option == "description":
            query = {"description": {"$regex": search_query, "$options": "i"}}
        elif search_option == "location":
            query = {"location": {"$regex": search_query, "$options": "i"}}
        elif search_option == "date":
            query = {"date": {"$regex": search_query, "$options": "i"}}
        docs = db["event"].find(query).sort("created_at", -1)
    else:
        docs = db["event"].find({}).sort("created_at", -1)
    return render_template("events.html", docs=docs)


@app.route("/add_event", methods=["GET", "POST"])
def add_event():
    if request.method == "POST":
        event_name = request.form.get("eventName")
        organizer = request.form.get("organizer")
        date = request.form.get("date")
        time = request.form.get("time")
        point_of_contact = request.form.get("pointOfContact")
        location = request.form.get("location")
        description = request.form.get("description")
        num_of_ppl = request.form.get("numOfPpl")

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
        db["event"].insert_one(new_event)
        return redirect(url_for("event"))

    return render_template("add_event.html")


@app.route("/profile")
def show_profile():
    if "userid" in session:
        id = session["userid"]
        user = db.users.find_one(
            {"_id": ObjectId(id)}
        )  # TODO : NEED TO RETRIEVE CURRENT USER FROM SESSION

        # myEvts = db.event.find_one({"_id": ObjectId("652f5cb3e3782d2a799feb73")}) #temp data
        # myPosting = db.event.find({}) #temp data

        myPostings = user["myPostings"]
        myEvents = user["myEvents"]

        print("MY POSTINGS",myPostings)
        for event in user["myEvents"]:
            if(event is not None):
                print(event)
                event_id = event["id"]
                event_details = db.event.find_one({"_id": ObjectId(event_id)})
                if(event_details is not None):
                    event.update(event_details)
                else:
                    myEvents = [event for event in myEvents if event.get("id") != ObjectId(event_id)]
                    print("After",myEvents)
                    update = {
                        "$set": {
                            "myEvents" : myEvents
                        }
                    }
                    db.users.update_one( {"_id": ObjectId(id)}, update)


        for event in user["myPostings"]:
            print("EVENT HERE", event)
            if(event is not None):
                event_id = event["id"]
                event_details = db.event.find_one({"_id": ObjectId(event_id)})
                print("EVENT DETAILS", event_details)
                if(event_details is not None):
                    event.update(event_details)
                else:
                    myPostings = [event for event in myPostings if event.get("id") != ObjectId(event_id)]
                    updatePostings = {
                        "$set": {
                        "myPostings" : myPostings
                    }
                    }
                    db.users.update_one({"_id": ObjectId(id)}, updatePostings)

                    print("THERE IS NOTHING HERE: DELETE FROM ARRAY")

        return render_template("profile.html", user=user)
    else:
        return redirect(url_for("loading"))
    


@app.route("/edit_user_info/<user_id>", methods=["GET", "POST", "PUT"])
def editUser(user_id):
    print("EDIT USER HELLO")
    if "userid" in session:
        id = session["userid"]
        
        user = db.users.find_one(
            {"_id": ObjectId(id)}
        )  # TODO : NEED TO RETRIEVE CURRENT USER FROM SESSION
       
       

        if request.method == "POST" or request.method == "PUT":
            name = request.form.get("fname")
            email = request.form.get("femail")
            password = request.form.get("fpassword")
            
            myquery = {"_id":ObjectId(user.get("_id"))}
            #print("before doc")
            doc = {

                "$set":
                { 
                    "name": name, 
                    "email": email, 
                    "password": password
                }
                    
            }

            #print(doc)
            db.users.update_one(myquery,doc)

            return redirect(url_for("show_profile"))
        
       
        return render_template("edit_user.html",user_id=user.get("_id"),user=user)
        
    else:
        return redirect(url_for("loading"))


@app.route('/editPosting/<post_id>', methods=["GET", "POST", "PUT"])
def editPosting(post_id):
    posting = db.event.find_one({"_id":ObjectId(post_id)})
    print("POSTING" , posting)
    if(request.method == "POST" or request.method == "POST"):
        eventName = request.form.get("eventName")
        organizer = request.form.get("organizer")
        date = request.form.get("date")
        time = request.form.get("time")
        pointOfContact = request.form.get("pointOfContact")
        description = request.form.get("description")
        location = request.form.get("location")
        numOfPpl = request.form.get("numOfPpl")

        doc = {
            "$set":
            {
            "eventName": eventName,
            "organizer": organizer,
            "date": date,
            "time": time,
            "pointOfContact": pointOfContact,
            "description": description,
            "location":location,
            "numOfPpl":numOfPpl
            }
        }

        db.event.update_one({"_id":ObjectId(post_id)}, doc)
        return redirect(url_for('show_profile'))


    return render_template('edit_posting.html',posting=posting)
    


@app.route('/delete/<user_id>/<event_id>')
def delete(user_id, event_id):
   
    #we also need to update user object and remove this from event array
    user = db.users.find_one({"_id":ObjectId(user_id)})
    myEvents = user["myEvents"] #myEvents array
    myPostings = user["myPostings"] #myPosting array

    #print("NEW PRINTS!")
    
    print("BEFORE: MY EVENTS",myEvents)
    
    #print(myPostings)

    #my events -> remove from list ONLY
   
    myEvents = [event for event in myEvents if event.get("id") != ObjectId(event_id)]
    print("After",myEvents)
    update = {
        "$set": {
            "myEvents" : myEvents
        }

    }

    db.users.update_one({"_id":ObjectId(user_id)}, update)
    #user["myEvents"] = myEvents
    print("USER UPDATE", user)
    
    #print("FOUND NONE FROM MY EVENT")

    #my posting-> remove from list AND database

    obj = False # a flag that indicates whether or not we need to delete from database
    for i in range(len(myPostings)):
        if(myPostings[i]['id'] == ObjectId(event_id)):
          obj = True
          break

    # remove from array
    myPostings = [event for event in myPostings if event.get("id") != ObjectId(event_id)]

    
    updatePostings = {
        "$set": {
            "myPostings" : myPostings
        }
    }

    db.users.update_one({"_id":ObjectId(user_id)}, updatePostings)

    # remove from database
    if(obj == True):
        db.event.delete_one({"_id":ObjectId(event_id)})

    


    return redirect(url_for('show_profile'))


######
# TO BE DELETED AFTER !! THIS IS FOR THE PURPOSE OF CREATING USER DATA
# SOME  DATA HERE IS HARD CODED
@app.route("/add_user", methods=["POST"])
def createUser():
    doc = {
        "name": "snow",
        "email": "snow@gmail.com",
        "password": "123&snow",
        "myEvents": [
            {"id": ObjectId("652f5ec73c5916795f01da0f")},
            {"id": ObjectId("653094223097ad79b94fea63")},
            {"id": ObjectId('65309856e3a691c4c135fd16')}
        ],
        "myPostings": [
            {"id": ObjectId("6530987ae3a691c4c135fd17")},
            ],
    }

    db.users.insert_one(doc)

    return doc
