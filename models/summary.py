from typing import List
from requests import Response

from libs.mailgun import Mailgun
from db import db


class SummaryModel(db.Model):
    __tablename__ = "summaries"  # this tells SQLAlchemy how to map to db table

    id = db.Column(db.Integer, primary_key=True)
    created_dt = db.Column(db.DateTime(), nullable=False)
    audio_file_name = db.Column(db.String(80), nullable=True)
    text = db.Column(db.String(1000), nullable=True)
    lang_code = db.Column(db.String(5), nullable=True)
    summary_marker = db.Column(db.String(20), nullable=True)
    customer_id = db.Column(db.Integer, db.ForeignKey("customers.id"), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False)
    user = db.relationship("UserModel")
    customer = db.relationship("CustomerModel")

    @classmethod
    def find_by_id(cls, id: int) -> "SummaryModel":
        return cls.query.filter_by(id=id).first()

    @classmethod
    def find_by_audio_name(cls, name: str) -> "SummaryModel":
        return cls.query.filter_by(audio_file_name=name).first()

    @classmethod
    def find_all(cls) -> List["SummaryModel"]:
        return cls.query.all()

    def send_summary_email(self) -> Response:
        subject = "Conversation Summary"
        customer_name = self.customer.fname + " " + self.customer.lname
        text1 = f"Hi {customer_name}, \n"
        text2 = f"Here is a summary from your last conversation with us on {str(self.created_dt)}: \n"
        footer = f"Best Regards and please contact us at anytime"
        text = text1 + text2 + self.text + "\n" + footer

        return Mailgun.send_email([self.customer.email], subject, text, html=None)


    def save_to_db(self) -> None:  # this works for both insert and update (upsert)
        db.session.add(self)  # this will insert from self.name and self.price.
        db.session.commit()

    def delete_from_db(self) -> None:
        db.session.delete(self)
        db.session.commit()
