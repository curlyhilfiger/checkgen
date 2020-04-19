from flask import Flask
from flask_sqlalchemy import SQLAlchemy

import redis
from rq import Queue
import os


app = Flask(__name__)


r = redis.Redis()
q = Queue(connection=r)

app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql://postgres:12345@localhost/test_check'
app.config['DEBUG'] = True
app.config['SESSION_COOKIE_SECURE'] = False
app.config['MEDIA_FOLDER'] = '/mnt/c/wsl/projects/checkge_api/app/media/pdf'


db = SQLAlchemy(app)

from app import views
from app import models
