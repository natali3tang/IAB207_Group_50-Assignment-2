from website import db, create_app
from website.models import *

app = create_app()
ctx = app.app_context()
ctx.push()
db.create_all()
