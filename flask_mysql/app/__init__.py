from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from config import app_config
import os


# create app
app = Flask(__name__, instance_relative_config=True)
config_name = os.getenv('FLASK_CONFIG')
app.config.from_object(app_config[config_name])
db = SQLAlchemy(app)

# imports
from app import routes, models, db_query, graph, errors
