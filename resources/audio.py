import logging
from flask_restful import Resource
from flask_uploads import UploadNotAllowed
from flask import send_file, request
from flask_jwt_extended import jwt_required, get_jwt_identity
import traceback
import os

from libs import audio_helper
from libs.strings import gettext
from schemas.audio import AudioSchema

logging.basicConfig(
    format='%(asctime)s %(levelname)8s [%(filename)s %(lineno)d] %(message)s',
    level=logging.DEBUG,
    datefmt='%d-%m-%Y %H:%M:%S', # this is an optional way of formatting the asctime variable
    filename='logs.txt')
logger = logging.getLogger("flask_app.resource_audio")


logger.debug('Beginning /schemas/audio.py')

audio_schema = AudioSchema()


class AudioUpload(Resource):
    @classmethod
    @jwt_required
    def post(cls):
        """
        Used to upload an audio file.
        It uses JWT to retrieve user information and then saves the audio to the users folder.
        If there is a filename conflict, it appends a number at the end.
        """

        logger.debug('Calling audio_schema.load')
        logger.debug(f"request.files = {request.files}")
        data = audio_schema.load(request.files)  # a dictionary in request with a key of file name and the data.
        # The data will always be a FileStorage object from werkzeug wrapped around the data.
        # i.e. {"audio": FileStorage} the name must be audio.
        logger.debug(f"data = {data}")
        logger.debug('Calling get_jwt_identity')
        user_id = get_jwt_identity()
        logger.debug(f'User_id is {user_id}')
        folder = f"user_{user_id}"  # /static/audios/user_1
        logger.debug(f'folder is {folder}')
        try:
            logger.debug(f'Starting try block')
            audio_path = audio_helper.save_audio(data["audio"], folder=folder)
            logger.debug(f'audio_path is {audio_path}')
            basename = audio_helper.get_basename(audio_path)
            logger.debug(f'basename is {basename}')
            logger.debug('Returning message...')
            return {"message": gettext("AUDIO_UPLOADED").format(basename)}, 201
        except UploadNotAllowed:
            extension = audio_helper.get_extension(data["audio"])
            return {"message": gettext("AUDIO_ILLEGAL_EXTENSION").format(extension)}, 400


class Audio(Resource):
    @classmethod
    @jwt_required
    def get(cls, filename: str):
        """
        Returns the requested audio if it exists. Looks up inside the logged in user's folder.
        """

        user_id = get_jwt_identity()
        folder = f"user_{user_id}"
        if not audio_helper.is_filename_safe(filename):
            return {"message": gettext("AUDIO_ILLEGAL_FILE_NAME").format(filename)}, 400
        try:
            return send_file(audio_helper.get_path(filename, folder=folder))
        except FileNotFoundError:
            return {"message": gettext("AUDIO_NOT_FOUND").format(filename)}, 404

    @classmethod
    @jwt_required
    def delete(cls, filename: str):
        user_id = get_jwt_identity()
        folder = f"user_{user_id}"

        if not audio_helper.is_filename_safe(filename):
            return {"message": gettext("AUDIO_ILLEGAL_FILE_NAME").format(filename)}, 400

        try:
            os.remove(audio_helper.get_path(filename, folder=folder))
            return {"message": gettext("AUDIO_DELETED").format(filename)}, 200
        except FileNotFoundError:
            return {"message": gettext("AUDIO_NOT_FOUND").format(filename)}, 404
        except:
            traceback.print_exc()
            return {"message": gettext("AUDIO_DELETE_FAILED").format(filename)}, 500
