import logging
from marshmallow import Schema, fields
from werkzeug.datastructures import FileStorage


logging.basicConfig(
    format='%(asctime)s %(levelname)8s [%(filename)s %(lineno)d] %(message)s',
    level=logging.DEBUG,
    datefmt='%d-%m-%Y %H:%M:%S', # this is an optional way of formatting the asctime variable
    filename='logs.txt')
logger = logging.getLogger(f"flask_app.schema_audio, the __name__ is: {__name__}")


# logger.debug('Beginning /schemas/audio.py')

class FileStorageField(fields.Field):
    logger.debug('Beginning class FileStorageField')
    default_error_messages = {
        "invalid": "Not a valid audio"
    }

    def _deserialize(self, value, attr, data, **kwargs)-> FileStorage:
        logger.debug('Calling deserialize')
        logger.debug(f'value is {value}')
        if value is None:
            return None

        if not isinstance(value, FileStorage):
            logger.debug('Calling self.fail()')
            self.fail("invalid")  # raises ValidationError

        logger.debug('returning value')
        return value


class AudioSchema(Schema):
    logger.debug('In AudioSchema, creating FileStorageField')
    audio = FileStorageField(required=True)
    logger.debug(f'audio is {audio}')
