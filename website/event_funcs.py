from flask import abort
from .models import Event, Location, Registration, EventGenre, EventStatus
from sqlalchemy import desc
from . import db
import os
from werkzeug.utils import secure_filename


# return event object from db and error check 404
def get_event(id):
    event = db.session.scalar(db.select(Event).where(Event.id == id))
    if event is None:
        abort(404)
    return event


def check_upload_file(form):
    fp = form.image.data
    filename = fp.filename  # what is stored in the DB
    BASE_PATH = os.path.dirname(__file__)
    upload_path = os.path.join(BASE_PATH, "static/img", secure_filename(filename))
    # store relative path in DB as image location in HTML is relative
    db_upload_path = "static/img/" + secure_filename(filename)
    fp.save(upload_path)
    return db_upload_path


def location_update(form, prev_location_id):
    # update new location and commit
    location = Location(
        street=form.street.data,
        suburb=form.suburb.data,
        city=form.city.data,
        postcode=form.postcode.data,
        state=form.state.data,
    )
    db.session.add(location)
    # return location id of the new location just created
    get_location_id = db.session.query(Location.id).order_by(desc(Location.id)).first()
    get_location_id = get_location_id[0]

    # delete previous location id from db
    old_location = db.session.query(Location).get(prev_location_id)
    if old_location:
        db.session.delete(old_location)
        db.session.commit()

    return get_location_id


def check_new_event_status(total_tickets, registration_count, event):
    # if the new event edit has same ticket num as registrations, change to full
    if total_tickets == registration_count:
        event.status_id = 2  # update status to full
        db.session.commit()
        print("Updated event status to full.")

    # if the event was previously full and the new edit has more reservations, change to open
    elif (event.status_id == 2) & (total_tickets > registration_count):
        event.status_id = 1  # update status to open
        db.session.commit()
        print("Updated event status to open")


# return what the order id for even registration will be
# i.e. latest order_id + 1
def get_order_id():
    order_id = db.session.scalar(
        db.select(Registration.id).order_by(desc(Registration.id))
    )
    order_id += 1
    return order_id


def get_filtered_events(current_user):
    filtered_events = []
    # filtering events by status, creator of the event, registered users for the event
    for event in Event.query.filter_by(status_id=1).all():
        if event.user_id != current_user.id and not is_user_registered(
            current_user, event
        ):
            filtered_events.append(event)
    return filtered_events


# subquery - checking if user has registered for the queried event
def is_user_registered(current_user, event):
    return any(
        registration.user_id == current_user.id for registration in event.registrations
    )
