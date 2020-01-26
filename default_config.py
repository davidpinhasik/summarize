import os

DEBUG = True

SQLALCHEMY_DATABASE_URI = os.environ.get("DATABASE_URI", "sqlite:///data.db")
SQLALCHEMY_TRACK_MODIFICATIONS = False
PROPAGATE_EXCEPTIONS = True
APP_SECRET_KEY="another-secret"
SECRET_KEY="yet-another-secret"
JWT_SECRET_KEY="a-very-secret-key"
UPLOADED_AUDIO_DEST = os.path.join("static", "audio")
JWT_BLACKLIST_ENABLED = True
JWT_BLACKLIST_TOKEN_CHECKS = ["access", "refresh"]
