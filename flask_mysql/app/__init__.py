from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_cors import CORS
from config import app_config
import nltk
import os


# create app
app = Flask(__name__, instance_relative_config=True)
CORS(app)
#config_name = os.getenv('FLASK_CONFIG')
config_name = "development"
app.config.from_object(app_config[config_name])
db = SQLAlchemy(app)

# download nltk corpus when starting flask if necessary
nltk.download('punkt')

# imports
from app import routes, models, db_query, graph, errors
