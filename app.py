import json

from flask import Flask, request, render_template, session, url_for, redirect

#dotenv import and load
from dotenv import load_dotenv
import os
load_dotenv()

#models
from models.user import User

#service
from service import *

#hash
import hashlib

#datetime & time
import datetime
import time

#google search & wiki
import pywhatkit as pwt

#create app
app = Flask(__name__)
app.secret_key = os.getenv("APP_SECRET_KEY")

#globals
isgoogle = False
isyoutube = False
isaddsecret = False
isremovesecret = False


#routes
@app.route("/")
def index():
    if "user" in session:
        user = session["user"]
        return render_template("home.html", user = user)
    return render_template("home.html")

@app.route("/login", methods=["POST", "GET"])
def login():
    if request.method == "POST":
        data = login_user(request.form["email"], hashlib.md5(request.form["password"].encode()).hexdigest())
        if data != -1:
            session["user"] = data.user
            return redirect(url_for("index"))

    if "user" not in session:
        return render_template("login.html")
    return redirect(url_for("index"))

@app.route("/register", methods=["POST", "GET"])
def register():
    if request.method == "POST":
        u = User()
        u.user = {
        "email" :request.form["email"],
        "firstname" :request.form["fname"],
        "lastname": request.form["lname"],
        "password" : hashlib.md5(request.form["password"].encode()).hexdigest(),
        "admin" : False,
        "secrets" : []
        }

        data = add_user(u)
        session["user"] = data.user
        user = session["user"]
        print(user)
        return redirect(url_for("index"))
   
    if "user" not in session:
        return render_template("register.html")
    return redirect(url_for("index"))

@app.route("/logout", methods=["GET"])
def log_out():
    global isgoogle
    global isyoutube
    global isaddsecret
    global isremovesecret
    isgoogle = False
    isyoutube = False
    isaddsecret = False
    isremovesecret = False
    session.clear()
    return redirect(url_for("index"))

#chat bot route
from chatbot.main import chat

#speak
from models.tts import _TTS

@app.route("/chatbot", methods=["GET"])
def chat_bot():
    if "user" in session:
        global isgoogle
        global isyoutube
        global isaddsecret
        global isremovesecret
        isgoogle = False
        isyoutube = False
        isaddsecret = False
        isremovesecret = False
        user = session["user"]
        return render_template("chatbot.html", user = user)
    else:
        return redirect(url_for("index"))

@app.route("/getmessage/<message>")
def get_message(message):
    if request.method == "GET":
        global isgoogle
        global isyoutube
        global isaddsecret
        global isremovesecret
        if(isgoogle):
            isgoogle = False
            try:
                pwt.search(message)
                say = "Searching..."
            except:
                say = "couldnt search."
        
        elif(isyoutube):
            isyoutube = False
            try:
                pwt.playonyt(message)
                say = "playing..."
            except:
                say = "couldnt play."
        
        elif(isaddsecret):
            isaddsecret = False
            worked = add_secret(session["user"]["_id"], message)
            if(worked):
                #update session
                session["user"] = get_user(session["user"]["_id"])
                say = "secret added"
            else:
                say = "couldnt add"

        elif(isremovesecret):
            isremovesecret = False
            worked = remove_secret(session["user"]["_id"], message)
            if(worked):
                #update session
                session["user"] = get_user(session["user"]["_id"])
                say = "secret removed"
            else:
                say = "couldnt find secret"

        else:
            res = chat(message)
            if(res["tag"] == "time"):
                now = datetime.datetime.now()
                response = now.strftime("%H:%M:%S")
                say = "Time is " + response
                return(say)
            elif(res["tag"] == "youtube"):
                isyoutube = True
                say = res["response"]
            elif(res["tag"] == "search"):
                isgoogle = True
                say = res["response"]
            elif(res["tag"] == "addsecret"):
                isaddsecret = True
                say = res["response"]
            elif(res["tag"] == "removesecret"):
                isremovesecret = True
                say = res["response"]
            elif(res["tag"] == "showsecrets"):
                say = session["user"]["secrets"]
            else:
                say = res["response"]
        
        tts = _TTS()
        tts.start(say)
        del(tts)
        return(str(say))


##admin routes
@app.route("/admin", methods=["GET"])
def admin():
    if "user" in session:
        user = session["user"]
        if user["admin"]:
            return render_template("admin.html", user = user)
    return redirect(url_for("index"))

@app.route("/usermng", methods=["GET"])
def user_mng():
    if "user" in session:
        user = session["user"]
        if user["admin"]:
            users = get_users()
            return render_template("usermng.html",user = user, users = users)
    return redirect(url_for("index"))

@app.route("/updateuser/<user_id>", methods=["POST", "GET"])
def user_update(user_id):
    if "user" in session:
        user = session["user"]
        if user["admin"]:
            if request.method == "GET":
                user_updated = get_user(user_id)
                print(user_updated)
                return render_template("register.html", user = user, user_updated = user_updated)
            else:
                #update
                u = User()
                try:
                    request.form["admin"]
                    u.user = {
                    "_id" : user_id,
                    "email" :request.form["email"],
                    "firstname" :request.form["fname"],
                    "lastname": request.form["lname"],
                    "admin" : True,
                    }
                except:
                    u.user = {
                    "_id" : user_id,
                    "email" :request.form["email"],
                    "firstname" :request.form["fname"],
                    "lastname": request.form["lname"],
                    "admin" : False 
                    }
                update_user(u)
                return redirect(url_for("user_mng"))

    return redirect(url_for("index"))

@app.route("/deleteuser/<user_id>", methods=["GET"])
def user_delete(user_id):
    if "user" in session:
        user = session["user"]
        if user["admin"]:
            delete_user(user_id)
            return redirect(url_for("user_mng"))

    return redirect(url_for("index"))

#app settings
if __name__ == "__main__":
    app.run(port=5000, debug=True)