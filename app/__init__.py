from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from dotenv import load_dotenv
from flask_jwt_extended import JWTManager
# from flask_cors import CORS
import os


load_dotenv()

database_url=os.getenv('DATA_BASE_URL')
app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = database_url
db = SQLAlchemy(app)
migrate = Migrate(app, db)
app.config['JWT_SECRET_KEY'] = os.getenv('JWT_SECRET_KEY')
jwt=JWTManager(app)
# CORS(app)






from app import routes