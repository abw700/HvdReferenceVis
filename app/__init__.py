from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_cors import CORS
from redis import Redis
from config import app_config
from worker import conn
import rq
import os


# create app
app = Flask(__name__, instance_relative_config=True)
CORS(app)
config_name = os.getenv('FLASK_CONFIG')
if config_name is None:
    raise ValueError('Environment variable for config name is missing')
app.config.from_object(app_config[config_name])
app.task_queue = rq.Queue(connection=conn)
app.rq_conn = conn
db = SQLAlchemy(app)

# imports
from app import routes, models, db_query, graph, errors