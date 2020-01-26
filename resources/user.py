import traceback
from flask_restful import Resource
from flask import request
from werkzeug.security import safe_str_cmp
from flask_jwt_extended import (
    jwt_required,
    create_access_token,
    create_refresh_token,
    jwt_refresh_token_required,
    fresh_jwt_required,
    get_jwt_identity,
    get_raw_jwt,
)

from models.user import UserModel
from schemas.user import UserSchema
from libs.mailgun import MailGunException
from libs.strings import gettext
from blacklist import BLACKLIST
from models.confirmation import ConfirmationModel
from security import encrypt_password, check_encrypted_password


user_schema = UserSchema()


class UserRegister(Resource):
    @classmethod
    def post(cls):
        user = user_schema.load(request.get_json())

        if not user.password:
            return {"message": gettext("USER_MISSING_PASSWORD")}, 400

        if not user.email:
            return {"message": gettext("USER_MISSING_EMAIL")}, 400

        if not user.soc_security_num:
            return {"message": gettext("USER_MISSING_SSN")}, 400

        if UserModel.find_by_username(user.username):
            return {"message": gettext("USER_EXISTS")}, 400

        if UserModel.find_by_email(user.email):
            return {"message": gettext("USER_EMAIL_ALREADY_EXISTS").format(user.email)}, 400

        if UserModel.find_by_ssn(user.soc_security_num):
            return {"message": gettext("USER_SSN_ALREADY_EXISTS").format(user.soc_security_num)}, 400

        try:
            hashed = encrypt_password(user.password)
            user.password = hashed
            user.save_to_db()
            confirmation = ConfirmationModel(user.id)
            confirmation.save_to_db()
            user.send_confirmation_email()
            return {"message": gettext("USER_SUCCESS_REGISTERED_MESSAGE")}, 201
        except MailGunException as e:
            user.delete_from_db()
            return {"message": str(e)}, 500
        except:
            traceback.print_exc()
            user.delete_from_db()
            return {"message": gettext("USER_FAILED_TO_CREATE_USER")}, 500


class User(Resource):
    @classmethod
    def get(cls, user_id: int):
        user = UserModel.find_by_id(user_id)
        if not user:
            return {"message": gettext("USER_NOT_FOUND")}, 404
        return user_schema.dump(user), 200

    @classmethod
    def delete(cls, user_id: int):
        user = UserModel.find_by_id(user_id)
        if not user:
            return {"message": gettext("USER_NOT_FOUND")}, 404
        user.delete_from_db()
        return {"message": gettext("USER_DELETED")}, 200


class UserLogin(Resource):
    @classmethod
    def post(cls):
        user_json = request.get_json()
        user_data = user_schema.load(user_json, partial=("email",))

        user = UserModel.find_by_username(user_data.username)

        # this is what the authenticate() function used to do.
        #  if user and safe_str_cmp(user.password, user_data.password):
        if user and check_encrypted_password(user_data.password, user.password):  #(password, hashed password)
            # identity= is what the identity() function used to do.
            confirmation = user.most_recent_confirmation
            if confirmation and confirmation.confirmed:
                access_token = create_access_token(identity=user.id, fresh=True)
                refresh_token = create_refresh_token(user.id)
                return {"access_token": access_token, "refresh_token": refresh_token}, 200

            if not confirmation:  # for users created via OAuth login i.e. GitHub
                access_token = create_access_token(identity=user.id, fresh=True)
                refresh_token = create_refresh_token(user.id)
                return {"access_token": access_token, "refresh_token": refresh_token}, 200

            return {"message": gettext("USER_NOT_CONFIRMED_ERROR").format(user.email)}, 400

        return {"message": gettext("USER_INVALID_CREDENTIALS")}, 401


class UserLogout(Resource):
    @classmethod
    @jwt_required
    def post(cls):
        jti = get_raw_jwt()["jti"]  # jti is "JWT ID", a unique identifier for a jwt
        BLACKLIST.add(jti)
        return {"message": gettext("USER_LOGOUT_SUCCESS")}, 200


class TokenRefresh(Resource):
    @classmethod
    @jwt_refresh_token_required
    def post(cls):
        current_user = get_jwt_identity()
        new_token = create_access_token(identity=current_user, fresh=False)
        return {"access_token": new_token}, 200

class SetPassword(Resource):
    @classmethod
    @fresh_jwt_required
    def post(cls):
        user_json = request.get_json()
        user_data = user_schema.load(user_json)  # username and new password
        user = UserModel.find_by_username(user_data.username)

        if not user:
            return {"message": gettext("USER_NOT_FOUND")}

        if not user_data.password:
            return {"message": gettext("USER_MISSING_PASSWORD")}, 400

        hashed = encrypt_password(user_data.password)
        user.password = hashed
        user.save_to_db()

        return {"message": gettext("USER_PASSWORD_UPDATED")}
