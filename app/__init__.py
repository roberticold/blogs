from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from dotenv import load_dotenv
from flask_jwt_extended import JWTManager
from flask_cors import CORS
from flask_mail import Mail
import os


load_dotenv()

database_url=os.getenv('DATA_BASE_URL')
app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = database_url
db = SQLAlchemy(app)
migrate = Migrate(app, db)
app.config['JWT_SECRET_KEY'] = os.getenv('JWT_SECRET_KEY')
jwt=JWTManager(app)
CORS(app)
app.config['MAIL_SERVER']= 'smtp.gmail.com'
app.config['MAIL_PORT']= 587
app.config['MAIL_USERNAME']= os.getenv('MAIL_USERNAME')
app.config['MAIL_PASSWORD']= os.getenv('MAIL_PASSWORD')
app.config['MAIL_USE_TLS']= True
mail=Mail(app)






from app import routes