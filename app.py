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


@app.route("/get_user")
def get_user():
    return render_template("users.html")


@app.route("/create_account", methods=["GET", "POST"])
def create_account():
    if request.method == "POST":
        existing_user = mongo.db.users.find_one(
            {"email": request.form.get("email")})

        if existing_user:
            flash("Email already registered. Please go to log in page.")
            return redirect(url_for("create_account"))

        user = {
            "name": request.form.get("name"),
            "email": request.form.get("email"),
            "password": generate_password_hash(request.form.get("password"))
        }
        mongo.db.users.insert_one(user)

        session["current_user"] = request.form.get("email")
        flash("Account registration successful!")
    return render_template("register.html")


@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        existing_user = mongo.db.users.find_one(
            {"email": request.form.get("email")})

        if existing_user:
            if check_password_hash(
                existing_user["password"], request.form.get("password")):
                    session["current_user"] = request.form.get("email")
                    name = mongo.db.users.find({"name": "name"})
                    flash("Hello, {}!".format(name))

            else:
                flash("Incorrect login details")
                return redirect(url_for("login"))

        else:
            flash("Incorrect login details")
            return redirect(url_for("login"))

    return render_template("login.html")


if __name__ == "__main__":
    app.run(host=os.environ.get("IP"),
            port=int(os.environ.get("PORT")),
            debug=os.environ.get("DEBUG"))
