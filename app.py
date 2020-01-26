import os
from flask import Flask, jsonify
from flask_restful import Api
from flask_jwt_extended import JWTManager
from flask_uploads import configure_uploads, patch_request_class
from flask_migrate import Migrate
from marshmallow import ValidationError
from dotenv import load_dotenv
import logging

load_dotenv(".env", verbose=True)  # important to load env variables before importing oa

from db import db
from ma import ma
from oa import oauth
from blacklist import BLACKLIST
from resources.user import UserRegister, User, UserLogin, UserLogout, TokenRefresh, SetPassword
from resources.summary import Summary, SummaryList
from resources.customer import Customer, CustomerList
from resources.confirmation import Confirmation, ConfirmationByUser
from resources.audio import AudioUpload, Audio
from resources.github_login import GithubLogin, GithubAuthorize
from libs.audio_helper import AUDIO_SET

logging.basicConfig(
    format='%(asctime)s %(levelname)8s [%(filename)s %(lineno)d] %(message)s',
    level=logging.INFO,
    datefmt='%d-%m-%Y %H:%M:%S', # this is an optional way of formatting the asctime variable
    filename='logs.txt')
logger = logging.getLogger(f"flask_app, the __name__ is: {__name__}")


app = Flask(__name__)
app.config.from_object("default_config")  # SQLALCHEMY_DATABASE_URI = "sqlite:///data.db"
# app.config.from_envvar("APPLICATION_SETTINGS")  # APPLICATION_SETTINGS=default_config.py (or config.py)
patch_request_class(app, 10 * 1024 * 1024)  # this is used to limit the maximum size of audios, 10MB max size upload
configure_uploads(app, AUDIO_SET)  # This activates the uploads for the AUDIO_SET that we have created, and if you
# have multiple sets, you would just call this multiple times. This links up the app with flask-uploads and #
# the AUDIO_SET.
logger.debug('Calling JWTManager(app)')
api = Api(app)
jwt = JWTManager(app)  # does not create the /auth endpoint
migrate = Migrate(app, db)


@app.errorhandler(ValidationError)
def handle_marshmallow_validation(err):
    logger.debug('Calling handle_marshmallow_validation')
    logger.debug(f'err.messages = {err.messages}')
    return jsonify(err.messages), 400
    # this is like an except ValidationError as err for all of our resources


@jwt.token_in_blacklist_loader
def check_if_token_in_blacklist(decrypted_token):
    return decrypted_token["jti"] in BLACKLIST


logger.debug('Calling api.add_resource...')
api.add_resource(Customer, "/customer/<string:email>")
api.add_resource(CustomerList, "/customers")
api.add_resource(Summary, "/summary/<string:audio_name>")
api.add_resource(SummaryList, "/summaries")
api.add_resource(UserRegister, "/register")  # this lists the route for resource UserRegister
api.add_resource(User, "/user/<int:user_id>")  # this lists the route for resource User
api.add_resource(UserLogin, "/login")
api.add_resource(UserLogout, "/logout")
api.add_resource(TokenRefresh, "/refresh")
api.add_resource(Confirmation, "/user_confirmation/<string:confirmation_id>")
api.add_resource(ConfirmationByUser, "/confirmation/user/<int:user_id>")
api.add_resource(AudioUpload, "/upload/audio")
api.add_resource(Audio, "/audio/<string:filename>")
api.add_resource(GithubLogin, "/login/github")
api.add_resource(GithubAuthorize, "/login/github/authorized", endpoint="github.authorize")
api.add_resource(SetPassword, "/user/password")


logger.debug('Calling main code')
if __name__ == "__main__":
    db.init_app(app)
    ma.init_app(app)
    oauth.init_app(app)
    app.run(port=5000)
