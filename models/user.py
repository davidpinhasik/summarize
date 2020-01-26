from requests import Response
from flask import request, url_for

from db import db
from libs.mailgun import Mailgun
from models.confirmation import ConfirmationModel


class UserModel(db.Model):
    __tablename__ = "users"

    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), nullable=False, unique=True)
    email = db.Column(db.String(80), nullable=True, unique=True)
    password = db.Column(db.String(120), nullable=True)
    soc_security_num = db.Column(db.String(9), nullable=True, unique=True)

    confirmation = db.relationship(
        "ConfirmationModel", lazy="dynamic", cascade="all, delete-orphan"
    )

    @property
    def most_recent_confirmation(self) -> "ConfirmationModel":
        return self.confirmation.order_by(db.desc(ConfirmationModel.expire_at)).first()

    def save_to_db(self) -> None:
        db.session.add(self)
        db.session.commit()

    def delete_from_db(self) -> None:
        db.session.delete(self)
        db.session.commit()

    @classmethod
    def find_by_username(cls, username: str) -> "UserModel":
        return cls.query.filter_by(username=username).first()
        # SQLAlchemy converts it to a UserModel object

    @classmethod
    def find_by_id(cls, _id: int) -> "UserModel":
        return cls.query.filter_by(id=_id).first()
        # SQLAlchemy converts it to a UserModel object

    @classmethod
    def find_by_email(cls, email: str) -> "UserModel":
        return cls.query.filter_by(email=email).first()
        # SQLAlchemy converts it to a UserModel object

    @classmethod
    def find_by_ssn(cls, ssn: str) -> "UserModel":
        return cls.query.filter_by(soc_security_num=ssn).first()
        # SQLAlchemy converts it to a UserModel object

    def send_confirmation_email(self) -> Response:
        link = request.url_root[:-1] + url_for(
            "confirmation", confirmation_id=self.most_recent_confirmation.id
        )
        subject = "Registration Confirmation"
        text = f"Please click on the link to confirm your registration: {link}"
        html = f'<html>Please click on the link to confirm your registration: <a href="{link}">link</a></html>'
        return Mailgun.send_email([self.email], subject, text, html)
