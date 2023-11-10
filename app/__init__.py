from flask import Flask
from dotenv import load_dotenv
import os
from flask_wtf.csrf import CSRFProtect

load_dotenv()
app = Flask(__name__)
app.config['SECRET_KEY'] = os.getenv('SECRET_KEY')

csrf = CSRFProtect(app)

from app import views