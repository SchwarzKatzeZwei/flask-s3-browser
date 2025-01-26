import os

from dotenv import load_dotenv

load_dotenv(verbose=True)

S3_BUCKET_NAME = os.environ.get("S3_BUCKET_NAME")
S3_ACCESS_KEY = os.environ.get("S3_ACCESS_KEY")
S3_SECRET_KEY = os.environ.get("S3_SECRET_KEY")
PASSWORD_LENGTH = int(os.environ.get("PASSWORD_LENGTH", "12"))

bind = f"{os.environ.get('FLASK_RUN_HOST')}:{os.environ.get('FLASK_RUN_PORT')}"
workers = 4
reload = True
preload_app = True
