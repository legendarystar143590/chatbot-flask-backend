import os
import uuid
import time
from dotenv import load_dotenv
from flask import Flask, request, jsonify, make_response
from flask_cors import CORS
from flask_migrate import Migrate
from flask_jwt_extended import JWTManager
from api.auth import user_blueprint
from api.bot import bot_blueprint
from api.knowledge import knowledge_blueprint
from api.chatlog import log_blueprint
from api.tickets import ticket_blueprint
from models import db, User
from datetime import timedelta

app = Flask(__name__)
# app.config['SQLALCHEMY_DATABASE_URI'] = os.getenv("DATABASE_URL")
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///database.db?check_same_thread=False&mode=WAL'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SQLALCHEMY_POOL_SIZE'] = 20
app.config['UPLOAD_FOLDER'] = os.getenv('UPLOAD_FOLDER')
app.config['JWT_SECRET_KEY'] = os.getenv('JWT_SECRET_KEY')

app.config['SECRET_KEY'] = os.getenv('JWT_SECRET_KEY')
app.config['MAIL_SERVER'] = 'smtp.googlemail.com'
app.config['MAIL_PORT'] = 587
app.config['MAIL_USE_TLS'] = True
app.config['MAIL_USERNAME'] = 'legendarystar2160187@gmail.com'
app.config['MAIL_PASSWORD'] = 'pksv wzbh wahl atbw'

app.config['JWT_ACCESS_TOKEN_EXPIRES'] = timedelta(minutes=15)
app.config['JWT_REFRESH_TOKEN_EXPIRES'] = timedelta(days=3)

# app.config['JWT_TOKEN_LOCATION'] = ['cookies']
# app.config['JWT_COOKIE_SECURE'] = True  # Set to False if not using https
# app.config['JWT_COOKIE_CSRF_PROTECT'] = True  # CSRF protection
# Initialize JWTManager
jwt = JWTManager(app)

db.init_app(app)
migrate = Migrate(app, db)
# CORS(app, supports_credentials=True, origins=['https://your-frontend-domain.com'])
CORS(app)

app.register_blueprint(user_blueprint, url_prefix='/api')
app.register_blueprint(bot_blueprint, url_prefix='/api')
app.register_blueprint(knowledge_blueprint, url_prefix='/api')
app.register_blueprint(log_blueprint, url_prefix='/api')
app.register_blueprint(ticket_blueprint, url_prefix='/api')

@app.route("/")
def index():
   db.create_all()
   # del_all_records()
   # print('Deleted')
   return "This is APIs for CustomGPT!"

if __name__ == '__main__':
   app.run(debug=True)
   
   