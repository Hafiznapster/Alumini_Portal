from datetime import datetime
from extensions import db

class Chat(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    last_message_at = db.Column(db.DateTime, default=datetime.utcnow)
    is_group_chat = db.Column(db.Boolean, default=False)
    group_name = db.Column(db.String(100))
    
    # For group chats, we need a many-to-many relationship with users
    participants = db.relationship('User', 
                                 secondary='chat_participants',
                                 backref=db.backref('chats', lazy='dynamic'),
                                 lazy='dynamic')
    
    # Relationship with messages
    messages = db.relationship('ChatMessage', backref='chat', lazy='dynamic')

# Association table for chat participants
chat_participants = db.Table('chat_participants',
    db.Column('chat_id', db.Integer, db.ForeignKey('chat.id'), primary_key=True),
    db.Column('user_id', db.Integer, db.ForeignKey('user.id'), primary_key=True),
    db.Column('joined_at', db.DateTime, default=datetime.utcnow)
)

class ChatMessage(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    chat_id = db.Column(db.Integer, db.ForeignKey('chat.id'), nullable=False)
    sender_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    content = db.Column(db.Text, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    is_read = db.Column(db.Boolean, default=False)
    
    # Relationship with sender
    sender = db.relationship('User', backref='sent_messages') 