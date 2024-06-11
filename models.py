from flask_sqlalchemy import SQLAlchemy
from flask import current_app
from sqlalchemy.sql import func
from datetime import datetime
from uuid import uuid4
from utils.common import get_language_name

db = SQLAlchemy()

class User(db.Model):
    __tablename__ = 'users'

    id = db.Column(db.Integer, primary_key=True, nullable = False, autoincrement = True)
    first_name = db.Column(db.String(255), nullable = True)
    last_name = db.Column(db.String(255), nullable = False)
    email = db.Column(db.String(255), unique = True, nullable = False)
    language = db.Column(db.String(255), unique = False, nullable = False)
    password = db.Column(db.String(255), nullable=False)
    mauticId = db.Column(db.String(255), nullable=False)
    botsActive = db.Column(db.String(255), nullable=False, default = 0)
    com_name = db.Column(db.String(255), nullable=False)
    com_vat = db.Column(db.String(255), nullable=False)
    com_street = db.Column(db.String(255), nullable=False)
    com_street_number = db.Column(db.String(255), nullable=False)
    com_city = db.Column(db.String(255), nullable=False)
    com_postal = db.Column(db.String(255), nullable=False)
    com_country = db.Column(db.String(255), nullable=False)
    com_website = db.Column(db.String(255), nullable=False)
    role = db.Column(db.String(255), nullable = False, default = 'user')
    created_at = db.Column(db.DateTime, nullable = False,  default=datetime.utcnow)
    
    def __init__(self, first_name, last_name, email, password, mauticId, botsActive, language, com_name, com_vat, com_street, com_street_number, com_city, com_postal, com_country, com_website):
        self.first_name = first_name
        self.last_name = last_name
        self.email = email
        self.password = password
        self.mauticId = mauticId
        self.botsActive = botsActive
        self.language = language
        self.com_name = com_name
        self.com_vat = com_vat
        self.com_street = com_street
        self.com_street_number = com_street_number
        self.com_city = com_city
        self.com_postal = com_postal
        self.com_country = com_country
        self.com_website = com_website
    
    # Add an index to the id column
    __table_args__ = (
        db.Index('idx_user_id', 'id'),
    )

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
        db_user = User.query.filter_by(id=name).first()
        return db_user
    
    @staticmethod
    def get_by_email(email):
        user = User.query.filter_by(email=email).first()
        return user


    def get_reset_token(self, expires_sec=1800): #<---HERE
        s=Serializer(current_app.config['SECRET_KEY'], expires_sec) #<---HERE
        return s.dumps({'user_id': self.id}).decode('utf-8') #<---HERE

    @staticmethod#<-- HERE-This means self is not an argument the function should expect
    def verify_reset_token(token): #<---HERE
        s=Serializer(current_app.config['SECRET_KEY']) #<---HERE
        try: #<---HERE
            user_id = s.loads(token)['user_id'] #<---HERE
        except: #<---HERE
            return None #<---HERE
        return Users.query.get(user_id) #<---HERE
    
    def json(self):
        return {
            'id': self.id,
            'first_name': self.first_name,
            'last_name': self.last_name,
            'email': self.email,
            'mauticId': self.mauticId,
            'botsActive': self.botsActive,
            'language': get_language_name(self.language),
            'password': self.password,  # Note: It's generally not safe to include password information here.
            'com_name': self.com_name,
            'com_vat': self.com_vat,
            'com_street': self.com_street,
            'com_street_number': self.com_street_number,
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
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    name = db.Column(db.String(255), nullable=True)
    avatar = db.Column(db.String(255), nullable=True)
    color = db.Column(db.String(255), nullable=False)
    active = db.Column(db.Integer, nullable=False)
    start_time = db.Column(db.String(255), nullable=False)
    end_time = db.Column(db.String(255), nullable=False)
    knowledge_base = db.Column(db.String(255), nullable=False)
    created_at = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)

    def __init__(self, user_id, name, avatar, color, active, start_time, end_time, knowledge_base):
        self.user_id = user_id
        self.name = name
        self.avatar = avatar
        self.color = color
        self.active = active
        self.start_time = start_time
        self.end_time = end_time
        self.knowledge_base = knowledge_base

    # Add an index to the name column
    __table_args__ = (
        db.Index('idx_bot_name', 'name'),
    )
    
    def save(self):
        db.session.add(self)
        db.session.commit()

    @staticmethod
    def get_by_id(bot_id):
        return Bot.query.filter_by(id=bot_id).first()
    
    @staticmethod
    def get_all_bots():
        return Bot.query.all()

    def json(self):
        return {
            'id': self.id,
            'name': self.name,
            'avatar': self.avatar,
            'color': self.color,
            'active': self.active == 1,
            'start_time': self.start_time,
            'end_time': self.end_time,
            'knowledge_base': self.knowledge_base,
            'created_at': self.created_at.isoformat()  # or strftime('%Y-%m-%d %H:%M:%S') for a specific format
        }

    def __repr__(self):
        return f"<Bot {self.name}>"

class DocumentKnowledge(db.Model):
    __tablename__ = 'documents'

    id = db.Column(db.Integer, primary_key=True, nullable=False, autoincrement=True)
    type = db.Column(db.String(255), nullable=False)
    filename = db.Column(db.String(255), nullable=False)
    unique_id = db.Column(db.String(255), nullable=False)
    created_at = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)

    def __init__(self, type, filename, unique_id):
        self.type = type
        self.filename = filename
        self.unique_id = unique_id
    
    def save(self):
        db.session.add(self)
        db.session.commit()

    @staticmethod
    def get_by_id(_id):
        return DocumentKnowledge.query.get(_id)

    @staticmethod
    def del_by_id(_id):
        document = DocumentKnowledge.get_by_id(_id)
        db.session.delete(document)
        db.session.commit()
        
    @staticmethod
    def get_all_documents():
        return DocumentKnowledge.query.all()

    def json(self):
        return {
            'id': self.id,
            'type': self.type,
            'filename': self.filename,
            'unique_id': self.unique_id,
            'created_at': self.created_at.isoformat()  # or strftime('%Y-%m-%d %H:%M:%S') for a specific format
        }

    def __repr__(self):
        return f"<DocumentKnowledge {self.name}>"

class Website(db.Model):
    __tablename__ = 'websites'
    id = db.Column(db.Integer, primary_key=True, nullable=False, autoincrement=True)
    url = db.Column(db.String(255), nullable=True)
    unique_id = db.Column(db.String(255), nullable=False)
    created_at = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)

    def __init__(self, url, unique_id):
        self.url = url
        self.unique_id = unique_id
    
    def save(self):
        db.session.add(self)
        db.session.commit()

    @staticmethod
    def get_by_id(id):
        return Website.query.get(id)
    
    @staticmethod
    def get_all_websites():
        return Website.query.all()

    def json(self):
        return {
            'id': self.id,
            'url': self.url,
            'unique_id': self.unique_id,
            'created_at': self.created_at.isoformat()  # or strftime('%Y-%m-%d %H:%M:%S') for a specific format
        }

    def __repr__(self):
        return f"<Website {self.name}>"

class Text(db.Model):
    __tablename__ = 'texts'

    id = db.Column(db.Integer, primary_key=True, nullable=False, autoincrement=True)
    question = db.Column(db.String(255), nullable=True)
    answer = db.Column(db.String(255), nullable=True)
    unique_id = db.Column(db.String(255), nullable=False)
    created_at = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)

    def __init__(self, question, answer, unique_id):
        self.question = question
        self.answer = answer
        self.unique_id = unique_id
    
    def save(self):
        db.session.add(self)
        db.session.commit()

    @staticmethod
    def get_by_id(id):
        return Text.query.get(id)
    
    @staticmethod
    def get_all_texts():
        return Text.query.all()

    def json(self):
        return {
            'id': self.id,
            'question': self.question,
            'answer': self.answer,
            'unique_id': self.unique_id,
            'created_at': self.created_at.isoformat()  # or strftime('%Y-%m-%d %H:%M:%S') for a specific format
        }

    def __repr__(self):
        return f"<Text {self.name}>"

class KnowledgeBase(db.Model):
    __tablename__ = 'knowledgebases'

    id = db.Column(db.Integer, primary_key=True, nullable=False, autoincrement=True)
    name = db.Column(db.String(255), nullable=False)
    unique_id = db.Column(db.String(255), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    created_at = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)

    def __init__(self, name, unique_id, user_id):
        self.name = name
        self.unique_id = unique_id
        self.user_id = user_id
    
    def save(self):
        db.session.add(self)
        db.session.commit()

    @staticmethod
    def get_by_id(id):
        return KnowledgeBase.query.get(id)
    
    @staticmethod
    def get_all_knowledgebases():
        return knowledgeBase.query.all()
    @staticmethod
    def delete_by_id(knowledgebase_id):
        knowledgebase = KnowledgeBase.get_by_id(knowledgebase_id)
        if knowledgebase:
            db.session.delete(knowledgebase)
            db.session.commit()
            return True
        return False


    def json(self):
        return {
            'id': self.id,
            'name': self.name,
            'user_id': self.user_id,
            'unique_id': self.unique_id,
            'created_at': self.created_at.isoformat()  # or strftime('%Y-%m-%d %H:%M:%S') for a specific format
        }

    def __repr__(self):
        return f"<KnowledgeBase {self.name}>"

class Conversation(db.Model):
    __tablename__ = 'conversations'

    id = db.Column(db.Integer, primary_key=True, nullable=False, autoincrement=True)
    user_message = db.Column(db.String(255), nullable=False)
    response = db.Column(db.String(255), nullable=False)
    session_id = db.Column(db.String(255), nullable=False)
    bot_id = db.Column(db.Integer, db.ForeignKey('bots.id'))
    created_at = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)

    def __init__(self, user_message, response, bot_id, session_id):
        self.user_message = user_message
        self.response = response
        self.bot_id = bot_id
        self.session_id = session_id
    
    def save(self):
        db.session.add(self)
        db.session.commit()

    @staticmethod
    def get_by_id(id):
        return Conversation.query.get(id).first()

    @staticmethod
    def get_latest_by_session(id):
        return Conversation.query.filter_by(session_id=id).order_by('created_at').limit(3).all()
    
    @staticmethod
    def get_by_session(id):
        return Conversation.query.filter_by(session_id=id).all()
    
    @staticmethod
    def get_all_texts():
        return Conversation.query.all()

    @classmethod
    def del_by_bot_id(cls, bot_id):
        """Deletes all conversations for a given bot_id"""
        try:
            num_rows_deleted = db.session.query(cls).filter(cls.bot_id == bot_id).delete()
            db.session.commit()
            return num_rows_deleted
        except Exception as e:
            db.session.rollback()
            raise e

    def json(self):
        return {
            'id': self.id,
            'user_message': self.user_message,
            'response': self.response,
            'session_id':self.session_id,
            'bot_id': self.bot_id,
            'created_at': self.created_at.isoformat()  # or strftime('%Y-%m-%d %H:%M:%S') for a specific format
        }

    def __repr__(self):
        return f"<Conversation {self.id}>"

class Order(db.Model):
    __tablename__ = 'orders'

    id = db.Column(db.Integer, primary_key=True, nullable=False, autoincrement=True)
    sessoin_id = db.Column(db.String(255), nullable=False)
    email = db.Column(db.String(255), nullable=False)
    status = db.Column(db.String(255), nullable=False)
    content = db.Column(db.String(255), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'))
    bot_name = db.Column(db.String(255), nullable=False)
    created_at = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)

    def __init__(self, sessoin_id, user_id, bot_name, email, status, content):
        self.sessoin_id = sessoin_id
        self.bot_name = bot_name
        self.user_id = user_id
        self.email = email
        self.status = status
        self.content = content
    
    def save(self):
        db.session.add(self)
        db.session.commit()

    @staticmethod
    def get_by_id(id):
        return Order.query.filter_by(id=id).first()

    @staticmethod
    def get_by_user(id):
        return Order.query.filter_by(user_id=id).all()
    
    @staticmethod
    def get_by_bot(name):
        return Order.query.filter_by(bot_name=name).all()
    
    @staticmethod
    def get_all_texts():
        return Order.query.all()

    @classmethod
    def del_by_user_id(cls, user_id):
        """Deletes all orders for a given user_id"""
        try:
            num_rows_deleted = db.session.query(cls).filter(cls.user_id == user_id).delete()
            db.session.commit()
            return num_rows_deleted
        except Exception as e:
            db.session.rollback()
            raise e
        
    @classmethod
    def del_by_id(cls, id):
        """Deletes all orders for a given id"""
        try:
            num_rows_deleted = db.session.query(cls).filter(cls.id == id).delete()
            db.session.commit()
            return num_rows_deleted
        except Exception as e:
            db.session.rollback()
            raise e

    def json(self):
        return {
            'id': self.id,
            'sessoin_id': self.sessoin_id,
            'email': self.email,
            'user_id': self.user_id,
            'bot_name': self.bot_name,
            'status': self.status,
            'content': self.content,
            'created_at': self.created_at.isoformat()  # or strftime('%Y-%m-%d %H:%M:%S') for a specific format
        }

    def __repr__(self):
        return f"<Order {self.id}>"
    
class ChatLog(db.Model):
    __tablename__ = 'chatlogs'

    id = db.Column(db.Integer, primary_key=True, nullable=False, autoincrement=True)
    session_id = db.Column(db.String(255), nullable=False)
    user_id = db.Column(db.String(255), nullable=False)
    bot_name = db.Column(db.String(255), nullable=False)
    created_at = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    ended_at = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)

    def __init__(self, user_id,  bot_name, session_id, created_at, ended_at):
        self.created_at = created_at
        self.ended_at = ended_at
        self.bot_name = bot_name
        self.user_id = user_id
        self.session_id = session_id
    
    def save(self):
        db.session.add(self)
        db.session.commit()

    @staticmethod
    def get_by_id(id):
        return ChatLog.query.get(id).first()

    @staticmethod
    def get_by_session(id):
        return ChatLog.query.filter_by(session_id=id).first()
    
    @staticmethod
    def get_by_user(id):
        return ChatLog.query.filter_by(user_id=id).all()
    
    @staticmethod
    def get_all_texts():
        return Conversation.query.all()

    @classmethod
    def del_by_bot_id(cls, bot_id):
        """Deletes all conversations for a given bot_id"""
        try:
            num_rows_deleted = db.session.query(cls).filter(cls.bot_id == bot_id).delete()
            db.session.commit()
            return num_rows_deleted
        except Exception as e:
            db.session.rollback()
            raise e

    def json(self):
        return {
            'id': self.id,
            'bot_name': self.bot_name,
            'user_id': self.user_id,
            'session_id': self.session_id,
            'created_at': self.created_at.isoformat(),  # or strftime('%Y-%m-%d %H:%M:%S') for a specific format
            'ended_at': self.ended_at.isoformat()
        }

    def __repr__(self):
        return f"<ChatLog {self.id}>"
