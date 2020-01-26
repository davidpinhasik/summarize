from datetime import datetime
import traceback

from flask_restful import Resource
from flask import request
from flask_jwt_extended import jwt_required, fresh_jwt_required, get_jwt_identity

from models.summary import SummaryModel
from schemas.summary import SummarySchema
from libs.strings import gettext
from libs.audio_helper import get_path
from sr import rec_speech

summary_schema = SummarySchema()
summary_list_schema = SummarySchema(many=True)


class Summary(Resource):
    # @jwt_required  # this can be either a fresh access token or a non fresh access token
    @classmethod
    def get(cls, audio_name: str):
        # note that for functions that we will not call in our code, but rather the function
        # will be called by a client, so there is no need to type hint for the returned type of the function
        summary = SummaryModel.find_by_audio_name(audio_name)

        if summary:
            return summary_schema.dump(summary), 200
        return {"message": gettext("SUMMARY_NOT_FOUND")}, 404

    @classmethod
    @fresh_jwt_required
    def post(cls, audio_name: str):
        if SummaryModel.find_by_audio_name(audio_name):
            return {"message": gettext("SUMMARY_NAME_ALREADY_EXISTS").format(audio_name)}, 400
        user_id = get_jwt_identity()
        folder = f"user_{user_id}"
        summary_json = request.get_json()

        summary = summary_schema.load(summary_json)
        summary.audio_file_name = audio_name
        summary.created_dt = datetime.now()
        file_name = get_path(filename=audio_name, folder=folder)
        # print(f"folder={folder}, audio_name={audio_name}, file_name={file_name}")
        summary.text = rec_speech(file_name, summary.lang_code).split(summary.summary_marker,1)[1]
        # summary.text = "TEMPORARY PLACEHOLDER FOR SPEECH TO TEXT SUMMARY"
        summary.user_id = user_id  # overides request json and takes from access token

        try:
            summary.save_to_db()
            summary.send_summary_email()
        except:
            traceback.print_exc()
            return {"message": gettext("SUMMARY_ERROR_INSERTING")}, 500

        return summary_schema.dump(summary), 201  # 201 is created

    @classmethod
    @jwt_required
    def delete(cls, audio_name: str):
        summary = SummaryModel.find_by_audio_name(audio_name)
        if summary:
            summary.delete_from_db()
            return {"message": gettext("SUMMARY_DELETED")}, 200
        return {"message": gettext("SUMMARY_NOT_FOUND")}, 404

    @classmethod
    @jwt_required
    def put(cls, audio_name: str):
        summary_json = request.get_json()
        print(f"summary_json={summary_json}")
        summary = SummaryModel.find_by_audio_name(audio_name)
        user_id = get_jwt_identity()
        summary.user_id = user_id
        folder = f"user_{user_id}"

        if summary is None:
            summary = summary_schema.load(summary_json)
            summary.audio_file_name = audio_name
            summary.created_dt = datetime.now()
            file_name = get_path(filename=audio_name, folder=folder)
            print(f"folder={folder}, audio_name={audio_name}, file_name={file_name}, lang_code={summary.lang_code}, marker={summary.summary_marker}")
            summary.text = rec_speech(file_name, summary.lang_code).split(summary.summary_marker, 1)[1]
        else:
            summary.created_dt = datetime.now()
            file_name = get_path(filename=audio_name, folder=folder)
            summary.lang_code = summary_json["lang_code"]
            summary.summary_marker = summary_json["summary_marker"]
            print(f"folder={folder}, audio_name={audio_name}, file_name={file_name}, lang_code={summary.lang_code}, marker={summary.summary_marker}")
            summary.text = rec_speech(file_name, summary.lang_code).split(summary.summary_marker, 1)[1]
            summary.customer_id = summary_json["customer_id"]

        summary.save_to_db()
        summary.send_summary_email()

        return summary_schema.dump(summary), 200


class SummaryList(Resource):
    @classmethod
    # @jwt_optional  # allows for providing partial functionality when not logged in
    def get(cls):
        summaries = summary_list_schema.dump(SummaryModel.find_all())
        return {"summaries": summaries}, 200
