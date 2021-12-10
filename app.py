import os
import json
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
def home():
    """
    Loads the homepage
    """
    return render_template("/pages/home.html")


@app.route("/wedding-party.html")
def wedding_party():
    """
    Loads the wedding party page
    """
    wedding_party = []
    with open("data/wedding-party.json", "r") as wedding_party_data:
        wedding_party = json.load(wedding_party_data)
    return render_template(
        "/pages/wedding-party.html", wedding_party=wedding_party)


@app.route("/register", methods=["GET", "POST"])
def register():
    """
    User can register for an account to submit their RSVP
    Checks if the username is already registered or not
    Redirects user to view their RSVP information
    """
    if request.method == "POST":
        existing_user = mongo.db.users.find_one(
            {"username": request.form.get("username").lower()})

        if existing_user:
            flash("Username already registered. Please go to log in page.")
            return redirect(url_for("register"))

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
            return redirect(url_for(
                "add_guest", user_id=user_id))

    return render_template(
        "/pages/authentication.html", register=True)


@app.route("/login", methods=["GET", "POST"])
def login():
    """
    Allows user to login to their RSVP account
        using their username and password details
    Redirects user to view their RSVP information
    """
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
                    "dashboard", user_id=session["user_id"]))

            else:
                flash("Incorrect Username and/or Password")
                return redirect(url_for("login"))

        else:
            flash("Incorrect Username and/or Password")
            return redirect(url_for("login"))

    return render_template("/pages/authentication.html")


@app.route("/dashboard/<user_id>", methods=["GET", "POST"])
def dashboard(user_id):
    """
    User landing page after login/account creation
    Displays users guests and rsvp information
    """
    guests = mongo.db.guests.find({"user_id": user_id})
    count_guests = guests.count()
    return render_template(
        "/pages/dashboard.html", user_id=user_id,
        guests=guests, count_guests=count_guests)


@app.route("/search", methods=["GET", "POST"])
def search():
    """
    User can search for guest by name
    """
    query = request.form.get("query")
    guests = mongo.db.guests.find({
        "$text": {"$search": query}}, allow_partial_results=True)
    count_guests = guests.count()
    user = mongo.db.users.find_one()
    user_id = user["_id"]
    return render_template(
        "/pages/dashboard.html", user_id=user_id,
        guests=guests, count_guests=count_guests)


@app.route("/add_guest/<user_id>", methods=["GET", "POST"])
def add_guest(user_id):
    """
    User can add a guest
    """
    food_choices = list(mongo.db.food_choices.find().sort([
        ("starter", 1),
        ("main", 1),
        ("dessert", 1)]))
    guests = mongo.db.guests.find({"user_id": user_id})
    if request.method == "POST":
        guest_details = {
            "user_id": request.form.get("user_id"),
            "full_name": request.form.get("full_name"),
            "attending_pre_meet": request.form.get("attending_pre_meet"),
            "attending_wedding": request.form.get("attending_wedding"),
            "starter": request.form.get("starter"),
            "main": request.form.get("main"),
            "dessert": request.form.get("dessert")
        }
        mongo.db.guests.insert_one(guest_details)
        flash("Guest succesfully added!")
        guest_details = mongo.db.guests.find_one({
            "full_name": request.form.get("full_name").lower(),
            "user_id": request.form.get("user_id")})
        count_guests = guests.count()
        return redirect(url_for(
            "dashboard", user_id=user_id,
            count_guests=count_guests, food_choices=food_choices))

    return render_template(
        "/components/forms/guest-details-form.html",
        user_id=user_id, food_choices=food_choices, add=True)


@app.route("/edit-guest/<guest_id>", methods=["GET", "POST"])
def edit_guest(guest_id):
    """
    User can edit/update guest information
    """
    user = mongo.db.users.find_one()
    user_id = user["_id"]
    guests = mongo.db.guests.find({"user_id": user_id})
    guest = mongo.db.guests.find_one({"_id": ObjectId(guest_id)})
    guest_id = guest["_id"]
    food_choices = list(mongo.db.food_choices.find().sort([
        ("starter", 1),
        ("main", 1),
        ("dessert", 1)]))
    if request.method == "POST":
        guest_details = {
            "user_id": request.form.get("user_id"),
            "full_name": request.form.get("full_name"),
            "attending_pre_meet": request.form.get("attending_pre_meet"),
            "attending_wedding": request.form.get("attending_wedding"),
            "starter": request.form.get("starter"),
            "main": request.form.get("main"),
            "dessert": request.form.get("dessert")
            }
        mongo.db.guests.update({"_id": ObjectId(guest_id)}, guest_details)
        flash("Guest succesfully edited!")
        guest_details = mongo.db.guests.find_one({
            "full_name": request.form.get("full_name").lower(),
            "user_id": request.form.get("user_id")})
        count_guests = guests.count()
        return redirect(url_for(
            "dashboard", user_id=user_id,
            count_guests=count_guests, food_choices=food_choices))

    return render_template(
        "/components/forms/guest-details-form.html",
        guest=guest, guest_id=guest_id,
        food_choices=food_choices, user_id=user_id)


@app.route("/delete_guest/<user_id>/<guest_id>")
def delete_guest(user_id, guest_id):
    """
    Allows the user to delete a guest
    Redirects the user back to the dashboard
    """
    # guests = mongo.db.guests.find({"user_id": user_id})
    mongo.db.guests.remove({'_id': ObjectId(guest_id)})
    # guest = mongo.db.guests.find_one({"user_id": user_id})
    # guest_id = guest["_id"]
    # count_guests = guests.count()
    flash("Guest successfully deleted")
    return redirect(url_for(
        "dashboard", user_id=user_id, guest_id=guest_id))


@app.route("/logout")
def logout():
    """
    Allows user to log out
    Clears user session
    Redirects user to login page
    """
    flash("You have been logged out")
    session.pop("user_id")
    return redirect(url_for("login"))


@app.route("/error")
def test_error():
    """
    Test to view the custom error page in the event of an error
    """
    return render_template('pages/error.html')


@app.errorhandler(404)
def page_not_found(error):
    """
    Renders error.html with 404 message
    """
    error_message = str(error)
    return render_template('pages/error.html',
                           error_message=error_message), 404


@app.errorhandler(500)
def server_error(error):
    """
    Renders error.html with 500 message.
    """
    error_message = str(error)
    return render_template('pages/error.html',
                           error_message=error_message), 500


if __name__ == "__main__":
    app.run(host=os.environ.get("IP"),
            port=int(os.environ.get("PORT")),
            debug=os.environ.get("DEBUG"))
