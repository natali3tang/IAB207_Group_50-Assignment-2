from flask import Blueprint, render_template, request, redirect, url_for, flash
from .models import (
    Event,
    User,
    Comment,
    Registration,
    Location,
    EventGenre,
    EventStatus,
)

from website.forms import (
    CreateForm,
    CommentForm,
    EventRegistrationForm,
    CancelEventForm,
    CancelRSVPForm,
    EditForm,
)
from sqlalchemy import and_, or_, desc, asc, func
from flask_login import login_required, current_user
from . import db
import os
from werkzeug.utils import secure_filename
from datetime import datetime
from .event_funcs import (
    get_event,
    check_upload_file,
    location_update,
    check_new_event_status,
    get_order_id,
)

bp = Blueprint("event", __name__, url_prefix="/events")


# SHOW EVENT BASED ON ID
@bp.route("/<id>", methods=["GET", "POST"])
def show(id):
    event = get_event(id)

    event_location = db.session.scalar(
        db.select(Location).where(event.location_id == Location.id)
    )
    event_status = db.session.scalar(
        db.select(EventStatus).where(EventStatus.id == event.status_id)
    )
    print(event_status.status)
    print(event_status.id)
    print(event_location)

    # querying for spots left available
    event_id = id
    participant_count = (
        db.session.query(Registration).filter(Registration.event_id == event_id).count()
    )
    ticket_num = event.total_tickets
    spots_left = ticket_num - participant_count

    user = db.session.scalar(db.select(User).where(event.user_id == User.id))

    if current_user.is_authenticated == False:
        user_created_form = False
        user_registered = False
        print("No logged in user")
    else:
        # checking if the logged in user (if a user is logged in) is the same as the user that created the event
        user_created_form = False
        if current_user.id == user.id:
            user_created_form = True  # bool storing this value
        # checking if the logged in user (if a user is logged in) has already registered for this event
        user_registered = True
        condition1 = Registration.user_id == current_user.id
        condition2 = Registration.event_id == event_id
        combined_condition = and_(condition1, condition2)
        reg_state = db.session.scalar(
            db.select(Registration.user_id).where(combined_condition)
        )
        if reg_state is None:
            user_registered = False

    commentForm = CommentForm()
    cancelForm = CancelRSVPForm()
    return render_template(
        "events/show.html",
        event=event,
        location=event_location,
        status=event_status,
        spots_left=spots_left,
        user=user,
        form=commentForm,
        user_created_form=user_created_form,
        user_registered=user_registered,
        cancel_form=cancelForm,
    )


# COMMENT ON AN EVENT
@bp.route("/<id>/comment", methods=["GET", "POST"])
@login_required
def comment(id):
    form = CommentForm()
    event = get_event(id)

    if form.validate_on_submit():
        comment = Comment(text=form.text.data, event=event, user=current_user)
        # using backreferencing here
        db.session.add(comment)
        db.session.commit()
        print("Your comment has been added", "success")
    return redirect(url_for("event.show", id=id))


# CREATE AN EVENT
@bp.route("/create", methods=["GET", "POST"])
@login_required
def create():
    print("Method type: ", request.method)
    error = None
    success = False
    form = CreateForm()
    print(current_user.id)
    if form.validate_on_submit() == True:
        start_time = form.start_time.data
        end_time = form.end_time.data
        if start_time >= end_time:
            error = "The event end time must be after the start time."
            print("Time error")
            flash(error)

        form_date = form.date.data
        current_datetime = datetime.now()
        current_date = current_datetime.date()
        if form_date <= current_date:
            error = "Event data cannot be a date in the past."
            print("Date error")
            flash(error)

        total_tickets = form.total_tickets.data
        if total_tickets <= 0:
            error = "The event must have more than 0 available tickets."
            print("Ticket error")
            flash(error)

        db_file_path = check_upload_file(form)

        if error is None:
            # form location
            location = Location(
                street=form.street.data,
                suburb=form.suburb.data,
                city=form.city.data,
                postcode=form.postcode.data,
                state=form.state.data,
            )
            db.session.add(location)
            db.session.commit()

            get_location = (
                db.session.query(Location).order_by(desc(Location.id)).first()
            )

            # form genre
            genre = form.genre.data
            get_genre_id = db.session.scalar(
                db.select(EventGenre.id).where(EventGenre.title == genre)
            )

            event = Event(
                title=form.title.data,
                date=form.date.data,
                start_time=form.start_time.data,
                end_time=form.end_time.data,
                total_tickets=form.total_tickets.data,
                description=form.description.data,
                image=db_file_path,
                age_limit=form.age_limit.data,
                user_id=current_user.id,
                location_id=get_location.id,
                genre_id=get_genre_id,
                status_id=1,  # initialised with a status of 1 --> OPEN
            )
            db.session.add(event)
            db.session.commit()
            flash("Your new event has been created successfully.", "success")
            # get_event = db.session.query(Event).order_by(desc(Event.id)).first()
            print("A new event has been created", "success")
            success = True
            return redirect(url_for("event.create"))

    return render_template(
        "events/create.html", form=form, success=success, edit_event=False
    )


# EDIT A PREVIOUSLY CREATED EVENT BASED ON ID
@bp.route("/<id>/edit", methods=["GET", "POST"])
@login_required
def edit(id):
    event = get_event(id)
    form = EditForm()
    error = None

    if form.validate_on_submit():
        # checking the registration count vs new input ticket number if changed
        registration_count = (
            db.session.query(Registration)
            .filter(Registration.event_id == event.id)
            .count()
        )
        if form.total_tickets.data < registration_count:
            if registration_count == 1:
                people_text = "person has"
            else:
                people_text = "people have"
            error = f"{registration_count} {people_text} currently registered for your event. You cannot change the number of tickets to {form.total_tickets.data}."
            flash(error)

        # check event start and end times
        start_time = form.start_time.data
        end_time = form.end_time.data
        if start_time >= end_time:
            error = "The event end time must be after the start time."
            print("Time error")
            flash(error)

        # check event date --> cannot be today or previous
        form_date = form.date.data
        current_datetime = datetime.now()
        current_date = current_datetime.date()
        if form_date <= current_date:
            error = "Event data cannot be a date in the past."
            print("Date error")
            flash(error)

        # tickets cannot be 0
        total_tickets = form.total_tickets.data
        if total_tickets <= 0:
            error = "The event must have more than 0 available tickets."
            print("Ticket error")
            flash(error)

        # DELETE THE PREVIOUS LOCATION AFTER THE NEW ONE HAS BEEN CREATED (location_update func.)
        if error is None:
            event_location_id = event.location_id
            get_new_location_id = location_update(form, event_location_id)

            # form genre
            genre = form.genre.data
            get_genre_id = db.session.scalar(
                db.select(EventGenre.id).where(EventGenre.title == genre)
            )

            # updating event attributes from new form input
            event.title = form.title.data
            event.date = form.date.data
            event.start_time = form.start_time.data
            event.end_time = form.end_time.data
            event.total_tickets = form.total_tickets.data
            event.description = form.description.data
            event.age_limit = form.age_limit.data
            event.user_id = current_user.id
            event.location_id = get_new_location_id
            event.genre_id = get_genre_id

            tickets = event.total_tickets

            # updating event status if new ticket num == total registrations
            check_new_event_status(tickets, registration_count, event)

            db.session.commit()
            flash("Your event has successfully been edited.")
            return redirect(url_for("event.create"))

    if request.method == "GET":
        # populate the form fields with event data
        form.title.data = event.title
        form.date.data = event.date
        form.start_time.data = event.start_time
        form.end_time.data = event.end_time
        form.total_tickets.data = event.total_tickets
        form.description.data = event.description
        form.age_limit.data = event.age_limit

        location = db.session.scalar(
            db.select(Location).where(Location.id == event.location_id)
        )
        genre = db.session.scalar(
            db.select(EventGenre).where(EventGenre.id == event.genre_id)
        )
        form.street.data = location.street
        form.suburb.data = location.suburb
        form.city.data = location.city
        form.postcode.data = location.postcode
        form.state.data = location.state
        form.genre.data = genre.title

    # passing in event details to generate data in form fields
    return render_template(
        "events/create.html", form=form, event=event, edit_event=True
    )


# REGISTER FOR AN EVENT
@bp.route("/<id>/register-for-event", methods=["GET", "POST"])
@login_required
def registration(id):
    form = EventRegistrationForm()
    event = get_event(id)
    event_location = db.session.scalar(
        db.select(Location).where(Location.id == Event.location_id)
    )

    # returning the order_id
    order_id = get_order_id()

    if form.validate_on_submit():
        print("Validate form")
        reg = Registration(
            registered_at=datetime.now(), user_id=current_user.id, event_id=event.id
        )
        db.session.add(reg)
        db.session.commit()

        # Checking whether event is full after registration and updating status if it is
        event_id = id
        participant_count = (
            db.session.query(Registration)
            .filter(Registration.event_id == event_id)
            .count()
        )
        ticket_num = db.session.scalar(
            db.select(Event.total_tickets).where(Event.id == event_id)
        )

        if participant_count == ticket_num:
            event.status_id = 2  # means FULL
            db.session.commit()
            print("Event status updated to FULL")

        flash(
            "You have successfully registered for the event '{0}', Order ID: {1}. Get excited!".format(
                event.title, reg.id
            ),
            "success",
        )
        return redirect(url_for("event.registered_events"))

    return render_template(
        "events/registration.html",
        form=form,
        event=event,
        user=current_user,
        location=event_location,
        order_id=order_id,
    )


# EVENT PARTICIPANTS TABLE
@bp.route("/<id>/participants", methods=["GET"])
@login_required
def participants(id):
    event = get_event(id)

    # return users who have registered for the event with <id>
    registered_users = (
        db.session.query(Registration).filter(Registration.event_id == event.id).all()
    )
    # print(registered_users[0].user.fname)
    return render_template(
        "events/participants.html",
        event=event,
        user=current_user,
        registered_users=registered_users,
    )


# SUMMARY OF REGISTERED EVENTS PAGE
@bp.route("/registered-events", methods=["GET"])
@login_required
def registered_events():
    # return registered upcoming events (full or open)
    upcoming_reg_events = (
        db.session.query(Event)
        .filter(or_(Event.status_id == 1, Event.status_id == 2))
        .filter(User.id == current_user.id)
        .filter(Registration.user_id == current_user.id)
        .order_by(asc(Event.date))
        .all()
    )

    # querying for the id of each of the events
    event_ids = [event.id for event in upcoming_reg_events]
    registration_ids = (
        db.session.query(Registration.id)
        .filter(Registration.user_id == current_user.id)
        .filter(Registration.event_id.in_(event_ids))
        .distinct()
        .all()
    )
    # joining both queries into one list
    upcoming_events_with_ids = zip(upcoming_reg_events, registration_ids)

    # return registered event history (inactive or cancelled)
    event_reg_history = (
        db.session.query(Event)
        .filter(or_(Event.status_id == 3, Event.status_id == 4))
        .filter(Registration.user_id == current_user.id)
        .order_by(asc(Event.date))
        .all()
    )

    # querying for the id of each of the events
    history_event_ids = [event.id for event in event_reg_history]
    history_registration_ids = (
        db.session.query(Registration.id)
        .filter(Registration.user_id == current_user.id)
        .filter(Registration.event_id.in_(history_event_ids))
        .distinct()
        .all()
    )
    # joining both queries into one list
    history_events_with_ids = zip(event_reg_history, history_registration_ids)

    form = CancelRSVPForm()

    # turning into a list so that html can check whether the lists are empty
    upcoming_events_with_ids = list(upcoming_events_with_ids)
    history_events_with_ids = list(history_events_with_ids)

    return render_template(
        "events/event_summary_registered.html",
        upcoming_events=upcoming_events_with_ids,
        event_history=history_events_with_ids,
        cancel_form=form,
        upcoming_reg_ids=registration_ids,
    )


# SUMMARY OF CREATED EVENTS PAGE
@bp.route("/created-events", methods=["GET"])
@login_required
def created_events():
    # get upcoming created events (full or open)
    upcoming_created_events = (
        db.session.query(Event)
        .filter(or_(Event.status_id == 1, Event.status_id == 2))
        .filter(Event.user_id == current_user.id)
        .order_by(asc(Event.date))
        .all()
    )

    # count registrations for each event
    registration_counts = (
        db.session.query(
            Registration.event_id, func.count().label("registration_count")
        )
        .group_by(Registration.event_id)
        .filter(
            Registration.event_id.in_([event.id for event in upcoming_created_events])
        )
        .all()
    )

    # map event ids to registration counts
    registration_counts_dict = {
        event_id: count for event_id, count in registration_counts
    }

    # combine events and reg counts
    upcoming_created_events_with_counts = [
        (event, registration_counts_dict.get(event.id, 0))
        for event in upcoming_created_events
    ]
    print(upcoming_created_events_with_counts)

    # return created event history (inactive or cancelled)
    created_event_history = (
        db.session.query(Event)
        .filter(or_(Event.status_id == 3, Event.status_id == 4))
        .filter(Event.user_id == current_user.id)
        .order_by(asc(Event.date))
        .all()
    )
    print(created_event_history)

    form = CancelEventForm()
    return render_template(
        "events/event_summary_created.html",
        upcoming_events=upcoming_created_events_with_counts,
        event_history=created_event_history,
        cancel_form=form,
    )


# EVENT CREATOR CANCELS AN EVENT
@bp.route("/<id>/cancel-event", methods=["GET", "POST"])
@login_required
def cancel(id):
    form = CancelEventForm()
    event = get_event(id)
    print(event)
    # cancel event and update status in db
    if form.validate_on_submit():
        event.status_id = 4
        print(event.status_id)
        db.session.commit()
        flash(f"Your event '{event.title}' has been successfully cancelled.")
    return redirect(url_for("event.created_events"))


# CANCEL EVENT REGISTRATION
@bp.route("/<id>/cancel-rego", methods=["GET", "POST"])
@login_required
def cancel_registration(id):
    form = CancelRSVPForm()
    event = get_event(id)
    print(event)
    # cancel registration and update status in db
    if form.validate_on_submit():
        user_condition = Registration.user_id == current_user.id
        reg_id_condition = Registration.event_id == event.id
        combined_condition = and_(user_condition, reg_id_condition)
        registration = db.session.scalar(
            db.select(Registration).where(combined_condition)
        )
        db.session.delete(registration)
        db.session.commit()
        flash(f"You are no longer registered for the event '{event.title}'.")
    return redirect(url_for("event.registered_events"))
