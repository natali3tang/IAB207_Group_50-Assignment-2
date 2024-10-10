from flask import Blueprint, flash, render_template, request, url_for, redirect
from werkzeug.security import generate_password_hash, check_password_hash

# from .models import User
from website.forms import LoginForm, User_RegisterationForm
from flask_login import login_user, login_required, logout_user
from . import db
from .models import *
from sqlalchemy import desc

# create a blueprint
bp = Blueprint("auth", __name__)


# LOGIN USER
@bp.route("/login", methods=["GET", "POST"])
def login():  # view function
    print("In Login View function")
    login_form = LoginForm()
    error = None
    if login_form.validate_on_submit() == True:
        email = login_form.email.data
        password = login_form.password.data
        user = db.session.scalar(db.select(User).where(User.email == email))
        if user is None:
            error = "Incorrect credentials supplied"
        elif not check_password_hash(
            user.password_hash, password
        ):  # takes the hash and password
            error = "Incorrect credentials supplied"
        if error is None:
            login_user(user)
            return redirect(url_for("main.index"))
        else:
            flash(error)
    return render_template("user.html", form=login_form)


# REGISTER USER
@bp.route("/register", methods=["GET", "POST"])
def register():
    reg_form = User_RegisterationForm()
    error = None
    if reg_form.validate_on_submit() == True:
        fname = reg_form.fname.data
        lname = reg_form.lname.data
        phonenum = reg_form.phonenum.data
        email = reg_form.email.data
        password = reg_form.password.data
        prevUser = db.session.scalar(db.select(User).where(User.email == email))
        if prevUser:
            error = "This email is already taken. Please use another."
            flash(error)
            return render_template("register.html", form=reg_form, error=error)
        if error is None:
            # form location
            location = Location(
                street=reg_form.street.data,
                suburb=reg_form.suburb.data,
                city=reg_form.city.data,
                postcode=reg_form.postcode.data,
                state=reg_form.state.data,
            )
            db.session.add(location)
            db.session.commit()
            get_location = (
                db.session.query(Location).order_by(desc(Location.id)).first()
            )

            pwd_hash = generate_password_hash(password)
            newUser = User(
                fname=fname,
                lname=lname,
                email=email,
                password_hash=pwd_hash,
                phonenum=phonenum,
                location_id=get_location.id,
            )
            db.session.add(newUser)
            db.session.commit()
            flash("You have successfully registered an account. Please login below.")
            return redirect(url_for("auth.login"))
        else:
            flash(error)
    else:
        return render_template("register.html", form=reg_form, error=error)


# LOGOUT USER
@bp.route("/logout")
@login_required
def logout():
    logout_user()
    return redirect(url_for("main.index"))
