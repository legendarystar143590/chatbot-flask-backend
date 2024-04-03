from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.sql import func
from datetime import datetime
from uuid import uuid4

db = SQLAlchemy()

class User(db.Model):
    __tablename__ = 'users'

    id = db.Column(db.Integer, primary_key=True, nullable = False, autoincrement = True)
    chat_id = db.Column(db.String(), nullable = True)
    name = db.Column(db.String(), nullable = False)
    email = db.Column(db.String(), unique = True, nullable = False)
    password = db.Column(db.String(), nullable = True)
    role = db.Column(db.String(), nullable = False, default = 'user')
    created_at = db.Column(db.DateTime, nullable = False,  default=datetime.utcnow)
    
    def __init__(self, name, email, password):
        self.name = name
        self.email = email
        self.password = password
    
    def register_user_if_not_exist(self):        
        db_user = User.query.filter(User.user_id == self.user_id).all()
        if not db_user:
            db.session.add(self)
            db.session.commit()
        return True
    
    def get_by_username(name):        
        db_user = User.query.filter(User.name == name).first()
        return db_user
    
    def json(self):
        return {'id': self.id, 'name':self.name}
    
    def __repr__(self):
        return f"<User {self.name}>"
