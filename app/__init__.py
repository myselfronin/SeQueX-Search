from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from dotenv import load_dotenv
import os
from flask_wtf.csrf import CSRFProtect
import logging

# Load environment variables
load_dotenv()

#Create app instance
app = Flask(__name__)

#Update app config
app.config['SECRET_KEY'] = os.getenv('SECRET_KEY')
app.config['SQLALCHEMY_DATABASE_URI'] = os.getenv('SQLALCHEMY_DATABASE_URI')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# Initialize CSRF protection
csrf = CSRFProtect(app)

# Initialize SQLAlchemy and Flask-Migrate
db = SQLAlchemy(app)
migrate = Migrate(app, db)

# Configure Logging
logger = logging.getLogger('myapp_logger')
logger.setLevel(logging.INFO)  # Adjust the level as needed

file_handler = logging.FileHandler('myapp.log')
file_handler.setLevel(logging.INFO)

formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
file_handler.setFormatter(formatter)

logger.addHandler(file_handler)


# Register all commands from the commands package
from app.commands import register_commands
register_commands(app)

from app import views
from .models import Papers