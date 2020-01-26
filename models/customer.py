from typing import List

from db import db


class CustomerModel(db.Model):
    __tablename__ = "customers"  # this tells SQLAlchemy how to map to db table

    id = db.Column(db.Integer, primary_key=True)
    lname = db.Column(db.String(30), nullable=True, unique=False)
    fname = db.Column(db.String(20), nullable=True, unique=False)
    email = db.Column(db.String(80), nullable=False, unique=True)

    summaries = db.relationship("SummaryModel", lazy="dynamic")

    @classmethod
    def find_by_email(cls, email) -> "CustomerModel":
        return cls.query.filter_by(email=email).first()

    @classmethod
    def find_all(cls) -> List["CustomerModel"]:  # just use for testing
        return cls.query.all()

    def save_to_db(self) -> None:
        db.session.add(self)
        db.session.commit()

    def delete_from_db(self) -> None:
        db.session.delete(self)
        db.session.commit()
