import os
from flask import (
    Flask, flash, render_template,
    redirect, request, session, url_for)
from flask_pymongo import PyMongo
from bson.objectid import ObjectId
from werkzeug.security import generate_password_hash, check_password_hash
if os.path.exists("env.py"):
    import env


app = Flask(__name__)

app.config["MONGO_DBNAME"] = os.environ.get("MONGO_DBNAME")
app.config["MONGO_URI"] = os.environ.get("MONGO_URI")
app.secret_key = os.environ.get("SECRET_KEY")

mongo = PyMongo(app)


@app.route("/")
def index():
    return render_template("index.html")


@app.route("/create_account", methods=["GET", "POST"])
def create_account():
    if request.method == "POST":
        existing_user = mongo.db.users.find_one(
            {"username": request.form.get("username").lower()})

        if existing_user:
            flash("Username already registered. Please go to log in page.")
            return redirect(url_for("create_account"))

        username = request.form.get("username").lower()
        password = generate_password_hash(request.form.get("password"))

        mongo.db.users.insert_one({
            'username': username,
            'password': password})

        flash("Account registration successful!")

        if mongo.db.users.find_one({"username": username}) is not None:
            user = mongo.db.users.find_one({"username": username})
            user_id = user["_id"]
            session["user_id"] = str(user_id)
            guests = mongo.db.guests.find({"user_id": user_id})
            count_guests = guests.count()
            return redirect(url_for(
                "view_rsvp", user_id=user_id, count_guests=count_guests))

    return render_template("register.html")


@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        existing_user = mongo.db.users.find_one(
            {"username": request.form.get("username").lower()})

        if existing_user:
            if check_password_hash(
                    existing_user["password"], request.form.get("password")):
                user_id = str(existing_user["_id"])
                session["user_id"] = str(user_id)
                flash("Hello, {}!".format(request.form.get("username")))
                return redirect(url_for(
                    "view_rsvp", user_id=session["user_id"]))

            else:
                flash("Incorrect Username and/or Password")
                return redirect(url_for("login"))

        else:
            flash("Incorrect Username and/or Password")
            return redirect(url_for("login"))

    return render_template("login.html")


@app.route("/view_rsvp/<user_id>", methods=["GET", "POST"])
def view_rsvp(user_id):
    guests = mongo.db.guests.find({"user_id": user_id})
    count_guests = guests.count()
    return render_template(
        "view_rsvp.html", user_id=user_id, count_guests=count_guests)


@app.route("/add_guest/<user_id>", methods=["GET", "POST"])
def add_guest(user_id):
    return render_template("add_guest.html", user_id=user_id)


@app.route("/logout")
def logout():
    flash("You have been logged out")
    session.pop("user_id")
    return redirect(url_for("login"))


if __name__ == "__main__":
    app.run(host=os.environ.get("IP"),
            port=int(os.environ.get("PORT")),
            debug=os.environ.get("DEBUG"))
