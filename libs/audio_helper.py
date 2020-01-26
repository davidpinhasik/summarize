import os
import re
from typing import Union
from werkzeug.datastructures import FileStorage

from flask_uploads import UploadSet, AUDIO

AUDIO_SET = UploadSet("audio", AUDIO)
""" set name will be called "audio"  and the accepted types will be AUDIO which are .wav, .mp3, .aac, .ogg, .oga, 
and .flac. When we upload an audio and put into this set (UploadSet("audio", AUDIO)) then it will be saved in
static/audio/audioname
"""


def save_audio(audio: FileStorage, folder: str = None, name: str = None) -> str:
    """Takes a FileStorage and saves it to a folder"""
    return AUDIO_SET.save(audio, folder, name)


def get_path(filename: str = None, folder: str = None) -> str:
    """Take image name and folder and return full path"""
    return AUDIO_SET.path(filename, folder)


def find_audio_any_format(filename: str, folder: str) -> Union[str, None,]:
    """Takes a filename and returns an audio on any of the accepted formats"""
    for _format in AUDIO:
        audio = f"{filename}.{_format}"
        audio_path = AUDIO_SET.path(filename=audio, folder=folder)
        if os.path.isfile(audio_path):
            return audio_path
    return None


def _retrieve_filename(file: Union[str, FileStorage]) -> str:
    """Take FileStorage and return the file name
    Allows our functions to call to call this with both file names AND fileStorages and always get back a file name
    """
    if isinstance(file, FileStorage):
        return file.filename
    return file


def is_filename_safe(file: Union[str, FileStorage]) -> bool:
    """Check our regex and return whether the string matches or not"""
    filename = _retrieve_filename(file)
    allowed_format = '|'.join(AUDIO)  # wav|mp3|aac|ogg|oga|flac
    regex = f"^[a-zA-Z0-9][a-zA-Z0-9_()-\.]*\.({allowed_format})$"
    return re.match(regex, filename) is not None


def get_basename(file: Union[str, FileStorage]) -> str:
    """Return full name of image in the path
    get_basename('some/folder/audio.wav') returns audio.wav
    """
    filename = _retrieve_filename(file)
    return os.path.split(filename)[1]  # returns the last part of path i.e. audio.wav


def get_extension(file: Union[str, FileStorage]) -> str:
    """Return file extension
    get_extension('audio.wav') returns '.wav'
    """
    filename = _retrieve_filename(file)
    return os.path.splitext(filename)[1]  # returns the last part of filename i.e. .wav

