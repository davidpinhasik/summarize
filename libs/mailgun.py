import os
from typing import List
from flask import request, url_for
from requests import Response, post

from libs.strings import gettext


class MailGunException(Exception):
    def __init__(self, message: str):
        super().__init__(message)

class Mailgun:
    MAILGUN_DOMAIN = os.environ.get("MAILGUN_DOMAIN")  # may be None
    MAILGUN_API_KEY = os.environ.get("MAILGUN_API_KEY")  # may be None

    FROM_TITLE = "Summarize REST API"
    FROM_EMAIL = "mailgun@sandboxb2997e7716914a6ebab1cd81eb5010a2.mailgun.org"

    @classmethod
    def send_email(cls, email: List[str], subject:str, text:str, html:str) -> Response:
        if cls.MAILGUN_API_KEY is None:
            raise MailGunException(gettext("MAILGUN_API_KEY_NOT_LOADED"))

        if cls.MAILGUN_DOMAIN is None:
            raise MailGunException(gettext("MAILGUN_DOMAIN_NOT_LOADED"))
        response =  post(
            f"https://api.mailgun.net/v3/{cls.MAILGUN_DOMAIN}/messages",
            auth=("api", cls.MAILGUN_API_KEY),
            data={"from": f"{cls.FROM_TITLE} <{cls.FROM_EMAIL}>",
                  "to": email,
                  "subject": subject,
                  "text": text,
                  "html": html
                  },
        )
        print(response.status_code)
        if response.status_code != 200:
            raise MailGunException(gettext("MAILGUN_CONF_EMAIL_ERROR"))
        return response
