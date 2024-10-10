from flask import Blueprint, render_template, request, redirect, url_for, abort
from flask_login import current_user
from .models import *
from .event_funcs import get_filtered_events

bp = Blueprint("main", __name__)


@bp.route("/")
def index():
    check_event_status()
    filter = None

    # clear previous search arguments
    request_args = request.args.to_dict()
    request_args.pop("search", None)

    # show all events (not logged in)
    if current_user.is_authenticated:
        events = get_filtered_events(current_user)

    # show events user has not created or registered in
    else:
        events = db.session.query(Event).filter(Event.status_id == 1).all()

    count = len(events)
    return render_template("index.html", events=events, filter=filter, count=count)


def check_event_status():
    current_date = datetime.now()
    # events become inactive on the day of (don't accept late registrations)
    events = db.session.query(Event).filter(Event.date <= current_date).all()
    for event in events:
        if event.status != 3:
            event.status_id = 3  # inactive event (in the past)
            print(f"Updating event {event} with new status INACTIVE")
            db.session.commit()


# event title based search
@bp.route("/search")
def search():
    search_query = request.args.get("search", "")
    if search_query:
        query = "%" + search_query + "%"
        events = db.session.query(Event).filter(Event.title.like(query)).all()
        count = len(events)
        return render_template(
            "index.html", events=events, search=True, query=search_query, count=count
        )
    else:
        return redirect(url_for("main.index"))


# sort by
@bp.route("/sort-by/<string:sort>")
def sort_by(sort):
    valid_sorts = ["date", "causes", "availability"]
    if sort not in valid_sorts:
        abort(401)

    if sort == "date":
        events = (
            db.session.query(Event)
            .filter(Event.status_id == 1)
            .order_by(Event.date)
            .all()
        )
        filter = "date"

    elif sort == "causes":
        events = (
            db.session.query(Event)
            .filter(Event.status_id == 1)
            .order_by(Event.genre_id)
            .all()
        )
        filter = "causes"

    elif sort == "availability":
        events = db.session.query(Event).order_by(Event.status_id).all()
        filter = "availability"

    count = len(events)
    return render_template("index.html", events=events, filter=filter, count=count)


# filter by state
@bp.route("/filter-state/<string:state>")
def filter_state(state):
    valid_states = ["QLD", "NSW", "TAS", "VIC", "WA", "SA", "ACT", "NT"]
    if state not in valid_states:
        abort(404)

    events = (
        db.session.query(Event)
        .filter(Event.status_id == 1)
        .join(Location)
        .filter(Location.state == state)
        .all()
    )
    filter = state
    count = len(events)
    return render_template("index.html", events=events, filter=filter, count=count)


# filter by cause
@bp.route("/filter-cause/<int:cause>")
def filter_cause(cause):
    if cause < 1 or cause > 8:
        abort(404)

    events = (
        db.session.query(Event)
        .filter(Event.status_id == 1)
        .filter(Event.genre_id == cause)
        .all()
    )

    genre = db.session.query(EventGenre.title).filter(EventGenre.id == cause).first()

    filter = genre[0]
    count = len(events)
    return render_template("index.html", events=events, filter=filter, count=count)
