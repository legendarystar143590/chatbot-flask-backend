from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.sql import func
from datetime import datetime
from uuid import uuid4

db = SQLAlchemy()

class User(db.Model):
    __tablename__ = 'users'

    id = db.Column(db.Integer, primary_key=True, nullable = False, autoincrement = True)
    first_name = db.Column(db.String(), nullable = True)
    last_name = db.Column(db.String(), nullable = False)
    email = db.Column(db.String(), unique = True, nullable = False)
    language = db.Column(db.String(), unique = False, nullable = False)
    password = db.Column(db.String(), nullable=False)
    com_name = db.Column(db.String(), nullable=False)
    com_vat = db.Column(db.String(), nullable=False)
    com_street = db.Column(db.String(), nullable=False)
    com_phone = db.Column(db.String(), nullable=False)
    com_city = db.Column(db.String(), nullable=False)
    com_postal = db.Column(db.String(), nullable=False)
    com_country = db.Column(db.String(), nullable=False)
    com_website = db.Column(db.String(), nullable=False)
    role = db.Column(db.String(), nullable = False, default = 'user')
    created_at = db.Column(db.DateTime, nullable = False,  default=datetime.utcnow)
    
    def __init__(self, first_name, last_name, email, password, language, com_name, com_vat, com_street, com_phone, com_city, com_postal, com_country, com_website):
        self.first_name = first_name
        self.last_name = last_name
        self.email = email
        self.password = password
        self.language = language
        self.com_name = com_name
        self.com_vat = com_vat
        self.com_street = com_street
        self.com_phone = com_phone
        self.com_city = com_city
        self.com_postal = com_postal
        self.com_country = com_country
        self.com_website = com_website
    
    def register_user_if_not_exist(self):        
        db_user = User.query.filter(User.email == self.email).all()
        if not db_user:
            db.session.add(self)
            db.session.commit()
            return True
        return False

    def save(self):
        db.session.commit()
    
    def get_by_userID(name):        
        db_user = User.query.filter(User.id == name).first()
        return db_user
    
    def json(self):
        return {
            'id': self.id,
            'first_name': self.first_name,
            'last_name': self.last_name,
            'email': self.email,
            'language': self.language,
            'password': self.password,  # Note: It's generally not safe to include password information here.
            'com_name': self.com_name,
            'com_vat': self.com_vat,
            'com_street': self.com_street,
            'com_phone': self.com_phone,
            'com_city': self.com_city,
            'com_postal': self.com_postal,
            'com_country': self.com_country,
            'com_website': self.com_website,
            'role': self.role
        }

    def __repr__(self):
        return f"<User {self.first_name}>"

class Bot(db.Model):
    __tablename__ = 'bots'

    id = db.Column(db.Integer, primary_key=True, nullable=False, autoincrement=True)
    name = db.Column(db.String(), nullable=True)
    avatar = db.Column(db.String(), nullable=False)
    color = db.Column(db.String(), nullable=False)
    active = db.Column(db.Integer, nullable=False)
    start_time = db.Column(db.String(), nullable=False)
    end_time = db.Column(db.String(), nullable=False)
    knowledge_base = db.Column(db.String(), nullable=False)
    created_at = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)

    def __init__(self, name, avatar, color, active, start_time, end_time, knowledge_base):
        self.name = name
        self.avatar = avatar
        self.color = color
        self.active = active
        self.start_time = start_time
        self.end_time = end_time
        self.knowledge_base = knowledge_base
    
    def save(self):
        db.session.add(self)
        db.session.commit()

    @staticmethod
    def get_by_id(bot_id):
        return Bot.query.get(bot_id)
    
    @staticmethod
    def get_all_bots():
        return Bot.query.all()

    def json(self):
        return {
            'id': self.id,
            'name': self.name,
            'avatar': self.avatar,
            'color': self.color,
            'active': self.active,
            'start_time': self.start_time,
            'end_time': self.end_time,
            'knowledge_base': self.knowledge_base,
            'created_at': self.created_at.isoformat()  # or strftime('%Y-%m-%d %H:%M:%S') for a specific format
        }

    def __repr__(self):
        return f"<Bot {self.name}>"