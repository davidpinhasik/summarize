from app import app
from db import db

db.init_app(app)

@app.before_first_request  # flask decorator that runs next commandbefore first request. creates tables if don't exsst
def create_tables():
    db.create_all()

