from flask import Blueprint, render_template, request, redirect, url_for, flash
from flask_login import current_user, login_required, login_user, logout_user
from models.connection import db
from models.model import User
from sqlalchemy import func
from models.model import ImageFile, ColorStat


auth = Blueprint("auth", __name__)

@auth.route("/login")
def login():
    return render_template("auth/login.html")

@auth.route("/login", methods=["POST"])
def login_post():
    email = request.form.get("email")
    password = request.form.get("password")
    remember = True if request.form.get("remember") else False

    user = User.query.filter_by(email=email).first()

    if not user or not user.check_password(password):
        flash("Please check your login details and try again.")
        return redirect(url_for("auth.login"))

    login_user(user, remember=remember)
    return redirect(url_for("auth.profile"))

    
@auth.route("/profile/edit", methods=["GET", "POST"])
@login_required
def edit_profile():
    if request.method == "POST":
        new_username = request.form.get("username")


    if new_username:
        current_user.username = new_username

    db.session.commit()
    flash("Profile updated successfully!")
    return redirect(url_for("auth.profile"))


    return render_template("auth/edit_profile.html", user=current_user)


from flask_login import current_user

@auth.route("/profile/delete", methods=["POST"])
@login_required
def delete_account():
    user = current_user._get_current_object() 
    logout_user()

    db.session.delete(user)
    db.session.commit()
    flash("Your account has been deleted.")
    return redirect(url_for("auth.signup"))


@auth.route("/profile")
@login_required
def profile():
    return render_template("auth/profile.html", user=current_user)
    

@auth.route("/signup")
def signup():
    return render_template("auth/signup.html")

@auth.route("/signup", methods=["POST"])
def signup_post():
    username = request.form["username"]
    email = request.form["email"]
    password = request.form["password"]

    if not username:
        flash("Invalid username")
        return redirect(url_for("auth.signup"))
    if not email:
        flash("Invalid email")
        return redirect(url_for("auth.signup"))
    if not password:
        flash("Invalid password")
        return redirect(url_for("auth.signup"))

    user = User.query.filter_by(email=email).first()
    if user:
        flash("User with this email address already exists")
        return redirect(url_for("auth.signup"))

    user = User(username=username, email=email)
    user.set_password(password)
    db.session.add(user)
    db.session.commit()

    return redirect(url_for("auth.login"))

@auth.route("/logout")
@login_required
def logout():
    logout_user()
    return render_template("auth/logout.html")
