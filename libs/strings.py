"""
lib.strings

By default, uses 'en-us.json' file inside the strings top level folder.

If language changes, then set 'libs.strings.default_locale' and run 'lib.strings.refresh()'
"""
import json

default_locale = "en-us"
cached_strings = {}

def refresh():
    global cached_strings
    with open(f"strings/{default_locale}.json") as f:
        cached_strings = json.load(f)


def gettext(name):
    return cached_strings[name]


def set_default_locale(locale):
    global default_locale
    default_locale = locale


refresh()

