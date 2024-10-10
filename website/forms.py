from flask_wtf import FlaskForm
from wtforms.fields import (
    TextAreaField,
    BooleanField,
    SubmitField,
    StringField,
    IntegerField,
    PasswordField,
    SelectField,
    DateField,
    TimeField,
)
from wtforms.validators import InputRequired, Length, Email, EqualTo
from flask_wtf.file import FileRequired, FileField, FileAllowed

ALLOWED_FILE = {"PNG", "JPG", "JPEG", "png", "jpg", "jpeg", "avif"}


# base event creation/edit form
class BaseForm(FlaskForm):
    title = StringField("Event Title", validators=[InputRequired("Enter event title")])
    date = DateField(
        "Date", validators=[InputRequired("Select a date")], render_kw={"type": "date"}
    )
    start_time = TimeField("Start Time", validators=[InputRequired("Select a time")])
    end_time = TimeField("End Time", validators=[InputRequired("Select a time")])
    total_tickets = IntegerField(
        "Tickets Available", validators=[InputRequired("Enter number of tickets")]
    )
    description = TextAreaField(
        "Description", validators=[InputRequired("Enter a short description")]
    )
    age_limit = BooleanField("18+ Event")
    street = StringField("Street", validators=[InputRequired("Enter a street address")])
    suburb = StringField("Suburb", validators=[InputRequired("Enter a suburb")])
    city = StringField("City", validators=[InputRequired("Enter a street address")])
    postcode = StringField("Postcode", validators=[InputRequired("Enter a post code")])
    state = SelectField(
        "State",
        choices=[
            ("QLD", "QLD"),
            ("NSW", "NSW"),
            ("TAS", "TAS"),
            ("WA", "WA"),
            ("SA", "SA"),
            ("ACT", "ACT"),
            ("NT", "NT"),
            ("VIC", "VIC"),
        ],
        validators=[InputRequired("Select a state")],
    )
    genre = SelectField(
        "Genre",
        choices=[
            ("Advocacy", "Advocacy"),
            ("Companionship", "Companionship"),
            ("Disaster Relief", "Disaster Relief"),
            ("Elderley", "Elderley"),
            ("Environment", "Environment"),
            ("Food and Water", "Food and Water"),
            ("Animals", "Animals"),
            ("Teaching and Learning", "Teaching and Learning"),
        ],
        validators=[InputRequired("Select a genre")],
    )


# create event form
class CreateForm(BaseForm):
    image = FileField(
        "Event Image",
        validators=[
            FileRequired(message="Image cannot be empty"),
            FileAllowed(ALLOWED_FILE, message="Only supports PNG, JPG, png, jpg, avif"),
        ],
    )
    submit = SubmitField("Create Event")


# edit event form
class EditForm(BaseForm):
    submit = SubmitField("Edit Event")


# this is event registration form
class EventRegistrationForm(FlaskForm):
    submit = SubmitField("Confirm Registration")


# this is cancel event form
class CancelEventForm(FlaskForm):
    submit = SubmitField("Cancel Event")


# this is cancel rsvp form
class CancelRSVPForm(FlaskForm):
    submit = SubmitField("Cancel RSVP")


# this is user emergency contact form
class EmergencyContactForm(FlaskForm):
    fname = StringField("First Name", validators=[InputRequired()])
    lname = StringField("Lirst Name", validators=[InputRequired()])
    email = StringField(
        "Email Address", validators=[Email("Please enter a valid email")]
    )
    phonenum = StringField("Phone Number", validators=[InputRequired()])


# creates the login information
class LoginForm(FlaskForm):
    email = StringField("Email Address", validators=[InputRequired("Enter user email")])
    password = PasswordField(
        "Password", validators=[InputRequired("Enter user password")]
    )
    submit = SubmitField("Login")


# this is the user registration form
class User_RegisterationForm(FlaskForm):
    fname = StringField("First Name", validators=[InputRequired()])
    lname = StringField("Last Name", validators=[InputRequired()])
    email = StringField(
        "Email Address", validators=[Email("Please enter a valid email")]
    )
    password = PasswordField(
        "Password", validators=[InputRequired("Please enter your password")]
    )
    confirm_password = PasswordField(
        "Confirm Password",
        validators=[
            InputRequired("Please re-enter your password"),
            EqualTo("password", message="Password must match"),
        ],
    )
    phonenum = StringField("Phone Number", validators=[InputRequired()])
    street = StringField("Street", validators=[InputRequired("Enter a street address")])
    suburb = StringField("Suburb", validators=[InputRequired("Enter a suburb")])
    city = StringField("City", validators=[InputRequired("Enter a street address")])
    postcode = StringField("Postcode", validators=[InputRequired("Enter a post code")])
    state = SelectField(
        "State",
        choices=[
            ("QLD", "QLD"),
            ("NSW", "NSW"),
            ("TAS", "TAS"),
            ("WA", "WA"),
            ("SA", "SA"),
            ("ACT", "ACT"),
            ("NT", "NT"),
            ("VIC", "VIC"),
        ],
        validators=[InputRequired("Select a state")],
    )
    submit = SubmitField("Register")


class CommentForm(FlaskForm):
    text = TextAreaField("Leave a Comment", [InputRequired()])
    submit = SubmitField("Post")
