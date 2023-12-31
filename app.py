from flask import (
    Flask,
    render_template,
    request,
    redirect,
    abort,
    url_for,
    make_response,
    session,
)
import pymongo
from bson.objectid import ObjectId
from pymongo import MongoClient
import os
import dotenv
from dotenv import load_dotenv
from datetime import datetime
from db import db
import sys

app = Flask(__name__)
app.secret_key = os.urandom(24)

if os.getenv("FLASK_ENV", "development") == "development":
    app.debug = True



@app.route("/")
def loading():
    if "userid" in session:
        return redirect(url_for("show_profile")) 
    else:
        return render_template("index.html", content="Greetings!")


# GET REQUESTS FOR LOG IN AND REGISTER


@app.route("/login", methods=["GET"])
def loginForm():
    # Check if user has just tried to log in and failed vis a vis a passed variable
    incorrect_login = request.args.get("incorrect_login", False)
    if "userid" in session:
        return redirect(url_for("show_profile")) 
    else:
        #Check if user has just tried to log in and failed vis a vis a passed variable
        incorrect_login = request.args.get('incorrect_login', False)

        return render_template("login.html", incorrect_login=incorrect_login)


@app.route("/register", methods=["GET"])
def registerForm():
    noPasswordMatch = request.args.get("noPasswordMatch", False)
    userExists = request.args.get("userExists", False)
    if "userid" in session:
        return redirect(url_for("show_profile")) 
    else:
        noPasswordMatch = request.args.get('noPasswordMatch', False)
        userExists = request.args.get('userExists', False)

    return render_template(
        "register.html", noPasswordMatch=noPasswordMatch, userExists=userExists
    )
    return render_template("register.html", noPasswordMatch = noPasswordMatch, userExists=userExists )


# POST REQUESTS FOR LOGIN AND REGISTER


@app.route("/login", methods=["POST"])
def processLogin():
    # Get the user enterd form data
    email = request.form["email"]
    password = request.form["password"]

    # Try to match the user entered email with a document in the database
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
        session["userid"] = str(getUser["_id"])
        session["email"] = email
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

    # check the user ented email is unique -> If not route back to register page with message
    getUser = db.users.find_one({"email": email})

    match = True
    if getUser == None:
        match = False

    if match:
        return render_template("register.html", userExists=True)

    # Check that passwords match -> if not route back to register page with message
    if password != confirmPassword:
        return render_template("register.html", noPasswordMatch=True)

    # Create an account in the database
    newAccount = {"email": email, "name": username, "password": password,"myEvents":[],"myPostings":[]}
    #newAccount = {"email": email, "name": username, "password": password,"myEvents":[{"_id":ObjectId("652f5ec73c5916795f01da0f")},{"_id":ObjectId("6530987ae3a691c4c135fd17")}],"myPostings":[]}

    db.users.insert_one(newAccount)
    user = db.users.find_one({"email":email})
    session["userid"] = str(user["_id"])
    session["email"] = email

    return redirect(url_for("event"))

@app.route("/logout")
def logout():
    if "userid" in session or "email" in session:
        session.pop("userid", None)
        session.pop("email", None)

    return redirect(url_for("loading"))


@app.route("/events", methods=["GET", "POST"])
def event():
    if "userid" in session:
        id = session["userid"]
        user = db.users.find_one({"_id":ObjectId(id)})
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
        return render_template("events.html", docs=docs, user=user)
    else:
        return redirect(url_for("loading"))

@app.route("/rsvp", methods=["POST"])
def rsvp():
    if "userid" not in session:
        return redirect(url_for("loading"))
    id = session["userid"]
    user = db.users.find_one({"_id": ObjectId(id)})
    event_id = request.form.get("event_id")
    events_collection = db["event"]
    event = events_collection.find_one({"_id": ObjectId(event_id)})
    docs = db["event"].find({}).sort("created_at", -1)

    print(event)
    #print("number of people", event["numOfPpl",type(event["numOfPpl"])])
    #print("capacity",event["capacity",type(event["capacity"])])

    if event["numOfPpl"] >= event["capacity"]:
        return render_template("events.html",docs=docs, capacity_overload=True, specific_event_id=ObjectId(event_id))
    elif any(str(e["_id"]) == event_id for e in user.get("myEvents", [])):
         print("already RSVP")
         return render_template("events.html",docs=docs, has_rsvpd=True, specific_event_id=ObjectId(event_id))
    else:
        events_collection.update_one({"_id": ObjectId(event_id)}, {"$inc": {"numOfPpl": 1}})
        user_events = user.get("myEvents", [])
        user_events.append({"_id": ObjectId(event_id)})
        db.users.update_one({"_id": ObjectId(id)}, {"$set": {"myEvents": user_events}})
    return redirect(url_for("event"))

@app.route("/add_event", methods=["GET", "POST"])
def add_event():
    if "userid" not in session:
        return redirect(url_for("loading"))
    id = session["userid"]
    user = db.users.find_one({"_id": ObjectId(id)})
    if request.method == "POST":
        event_name = request.form.get("eventName")
        organizer = request.form.get("organizer")
        date = request.form.get('date')
        time = request.form.get('time')
        point_of_contact = request.form.get("pointOfContact")
        location = request.form.get("location")
        description = request.form.get("description")
        capacity = int(request.form.get("capacity"))

        new_event = {
            "eventName": event_name,
            "created_at": datetime.now(),
            "organizer": organizer,
            "date": date,
            "time": time,
            "pointOfContact": point_of_contact,
            "location": location,
            "description": description,
            "capacity": capacity,
            "numOfPpl": 0,
        }
        db["event"].insert_one(new_event)
        event_id= ObjectId(new_event["_id"])
        user_postings= user.get("myPostings", [])
        user_postings.append({"_id": ObjectId(event_id)})
        db.users.update_one({"_id": ObjectId(id)}, {"$set": {"myPostings": user_postings}})
        return redirect(url_for("event"))
    return render_template("add_event.html",user=user)


@app.route("/profile")
def show_profile():
    if "userid" in session:
        id = session["userid"]
        user = db.users.find_one(
            {"_id": ObjectId(id)}
        ) 

        myPostings = user["myPostings"]
        myEvents = user["myEvents"]

        print("MY POSTINGS", myPostings)
        for event in user["myEvents"]:
            if event is not None:
                print(event)
                event_id = event["_id"]
                event_details = db.event.find_one({"_id": ObjectId(event_id)})
                if event_details is not None:
                    event.update(event_details)
                else:
                    myEvents = [event for event in myEvents if event.get("_id") != ObjectId(event_id)]
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
                event_id = event["_id"]
                event_details = db.event.find_one({"_id": ObjectId(event_id)})
                print("EVENT DETAILS", event_details)
                if event_details is not None:
                    event.update(event_details)
                else:
                    myPostings = [event for event in myPostings if event.get("_id") != ObjectId(event_id)]
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
        )  
       
       

        if request.method == "POST" or request.method == "PUT":
            name = request.form.get("fname")
            email = request.form.get("femail")
            password = request.form.get("fpassword")

            myquery = {"_id": ObjectId(user.get("_id"))}
            # print("before doc")
            doc = {"$set": {"name": name, "email": email, "password": password}}

            # print(doc)
            db.users.update_one(myquery, doc)

            return redirect(url_for("show_profile"))

        return render_template("edit_user.html", user_id=user.get("_id"), user=user)

    else:
        return redirect(url_for("loading"))


@app.route("/editPosting/<post_id>", methods=["GET", "POST", "PUT"])
def editPosting(post_id):
    if "userid" in session:
        user = db.users.find_one({"_id":ObjectId(session["userid"])})
        posting = db.event.find_one({"_id":ObjectId(post_id)})
        print("POSTING" , posting)
        if(request.method == "PUT" or request.method == "POST"):
            eventName = request.form.get("eventName")
            organizer = request.form.get("organizer")
            date = request.form.get("date")
            time = request.form.get("time")
            pointOfContact = request.form.get("pointOfContact")
            description = request.form.get("description")
            location = request.form.get("location")
            numOfPpl = int(request.form.get("capacity"))

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
                "capacity":numOfPpl,
                }
            }

            db.event.update_one({"_id":ObjectId(post_id)}, doc)
            return redirect(url_for('show_profile'))
        return render_template('edit_posting.html',posting=posting,user=user)
    else:
        return redirect(url_for('loading'))
    
    

@app.route("/delete/<user_id>/<event_id>")
def delete(user_id, event_id):
   
   if "userid" in session:
        print("PRINT IDS", user_id,session["userid"] )
        #we also need to update user object and remove this from event array
        user = db.users.find_one({"_id":ObjectId(user_id)})
        myEvents = user["myEvents"] #myEvents array
        myPostings = user["myPostings"] #myPosting array

        #print("NEW PRINTS!")
        
        print("BEFORE: MY EVENTS",myEvents)
        print()
        print()
        print(event_id)
        
        #print(myPostings)

        for i in range(len(myEvents)):
            if(myEvents[i]["_id"] == ObjectId(event_id)):
                print("HOHO",myEvents[i]["_id"])
                db.event.update_one({"_id":ObjectId(myEvents[i]["_id"])},
                    {"$inc": {"numOfPpl": -1}}
                )
                myEvents.remove(myEvents[i])
                break



        #myEvents = [event for event in myEvents if event.get("_id") != ObjectId(event_id)]
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
            if(myPostings[i]['_id'] == ObjectId(event_id)):
                obj = True
                break

         #my events -> remove from list ONLY
        #print(myPostings[0].get("_id") != event_id)
        #print(myPostings[1].get("_id") != event_id)
        # remove from array
        myPostings = [event for event in myPostings if event.get("_id") != ObjectId(event_id)]

        
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
   
   else:
       return redirect(url_for('loading'))


