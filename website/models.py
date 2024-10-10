from . import db
from flask_login import UserMixin
from datetime import datetime


# EmergencyContact
class EmergencyContact(db.Model):
    __tablename__ = "emergencyContacts"
    id = db.Column(db.Integer, primary_key=True)
    fname = db.Column(db.String(80), nullable=False)
    lname = db.Column(db.String(80), nullable=False)
    email = db.Column(db.String(100), unique=True, nullable=False)
    phonenum = db.Column(db.String(20), nullable=False)

    # foreign key
    user_id = db.Column(db.Integer, db.ForeignKey("users.id"))

    def __repr__(self):
        return f"<EmergencyContact: {self.id}, {self.fname} {self.lname}, {self.email}>"


# Waitlist
class Waitlist(db.Model):
    __tablename__ = "waitlists"
    id = db.Column(db.Integer, primary_key=True)
    position_num = db.Column(db.Integer)
    joined_at = db.Column(db.DateTime, default=datetime.now())

    # foreign keys
    user_id = db.Column(db.Integer, db.ForeignKey("users.id"))
    event_id = db.Column(db.Integer, db.ForeignKey("events.id"))

    def __repr__(self):
        return f"<Waitlist: {self.id}, position {self.position_num}, {self.joined_at}>"


# Event Status
class EventStatus(db.Model):
    __tablename__ = "status"
    id = db.Column(db.Integer, primary_key=True)
    status = db.Column(db.String(20), nullable=False)

    def __repr__(self):
        return f"<EventStatus: {self.id} {self.status}>"


# Event Genre
class EventGenre(db.Model):
    __tablename__ = "genres"
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(30), nullable=False)

    def __repr__(self):
        return f"<EventGenre: {self.id} {self.title}>"


# Registration Info
class Registration(db.Model):
    __tablename__ = "registrations"
    id = db.Column(db.Integer, primary_key=True)
    registered_at = db.Column(db.DateTime, default=datetime.now())

    # foreign keys
    user_id = db.Column(db.Integer, db.ForeignKey("users.id"))
    event_id = db.Column(db.Integer, db.ForeignKey("events.id"))

    def __repr__(self):
        return f"<Registration: registered at {self.registered_at} with id {self.id}>"


# Comments
class Comment(db.Model):
    __tablename__ = "comments"
    id = db.Column(db.Integer, primary_key=True)
    text = db.Column(db.String(400), nullable=False)
    posted_at = db.Column(db.DateTime, default=datetime.now())

    # foreign keys
    user_id = db.Column(db.Integer, db.ForeignKey("users.id"))
    event_id = db.Column(db.Integer, db.ForeignKey("events.id"))

    def __repr__(self):
        return f"<Comment: {self.text}, posted at {self.posted_at}>"


# Location
class Location(db.Model):
    __tablename__ = "locations"
    id = db.Column(db.Integer, primary_key=True)
    street = db.Column(db.String(50), nullable=False)
    suburb = db.Column(db.String(50), nullable=False)
    city = db.Column(db.String(50), nullable=False)
    postcode = db.Column(db.Integer, nullable=False)
    state = db.Column(db.String(5), nullable=False)

    events = db.relationship("Event", backref="location")
    users = db.relationship("User", backref="location")

    def __repr__(self):
        return f"<Location: {self.street} {self.suburb} {self.city} {self.postcode} {self.state}>"


# User
class User(db.Model, UserMixin):
    __tablename__ = "users"
    id = db.Column(db.Integer, primary_key=True)
    fname = db.Column(db.String(80), nullable=False)
    lname = db.Column(db.String(80), nullable=False)
    email = db.Column(db.String(100), unique=True, nullable=False)
    password_hash = db.Column(db.String(255), nullable=False)
    phonenum = db.Column(db.String(20), nullable=False)

    location_id = db.Column(db.Integer, db.ForeignKey("locations.id"))

    # backrefs
    comments = db.relationship("Comment", backref="user")
    created_events = db.relationship("Event", backref="user")
    registered_events = db.relationship("Registration", backref="user")
    emergency_contact = db.relationship("EmergencyContact", backref="user")
    waitlists = db.relationship("Waitlist", backref="user")
    locations = db.relationship("Location", backref="user")

    def __repr__(self):
        return f"<User: {self.id} + {self.fname} + {self.lname}, {self.email}>"


# Event
class Event(db.Model):
    __tablename__ = "events"
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(100), nullable=False)
    date = db.Column(db.Date, nullable=False)
    start_time = db.Column(db.Time, nullable=False)
    end_time = db.Column(db.Time, nullable=False)
    total_tickets = db.Column(db.Integer, nullable=False)
    description = db.Column(db.String(500), nullable=False)
    image = db.Column(
        db.String(400), default="static/img/generic.jpg"
    )  # have a local generic image for users who don't upload a photo
    age_limit = db.Column(db.Boolean, default=False)

    # foreign keys
    user_id = db.Column(db.Integer, db.ForeignKey("users.id"))
    location_id = db.Column(db.Integer, db.ForeignKey("locations.id"))
    genre_id = db.Column(db.Integer, db.ForeignKey("genres.id"))
    status_id = db.Column(db.Integer, db.ForeignKey("status.id"))

    # backrefs
    waitlists = db.relationship("Waitlist", backref="event")
    registrations = db.relationship("Registration", backref="event")
    comments = db.relationship("Comment", backref="event")
    locations = db.relationship("Location", backref="event", foreign_keys=[location_id])
    genres = db.relationship("EventGenre", backref="event")
    status = db.relationship("EventStatus", backref="event")

    def __repr__(self):
        return f"<Event: {self.title}, {self.date}, {self.start_time} - {self.end_time}, {self.total_tickets} available>"
