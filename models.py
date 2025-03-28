from flask_login import UserMixin
from datetime import datetime
from extensions import db

class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(100), unique=True, nullable=False)
    password = db.Column(db.String(200), nullable=False)
    name = db.Column(db.String(100), nullable=False)
    graduation_year = db.Column(db.Integer, nullable=False)
    degree = db.Column(db.String(100))
    major = db.Column(db.String(100))
    role = db.Column(db.String(20), default='user')
    bio = db.Column(db.Text)
    profile_pic = db.Column(db.String(200), default='default.jpg')
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    is_admin = db.Column(db.Boolean, default=False)
    mentor_status = db.Column(db.Boolean, default=False)
    mentor_fields = db.Column(db.String(100))
    mentor_bio = db.Column(db.Text)
    
    # Relationships
    events = db.relationship('EventRegistration', back_populates='user')
    job_posts = db.relationship('JobPost', backref='author', lazy=True)
    forum_posts = db.relationship('ForumPost', backref='author', lazy=True)
    forum_comments = db.relationship('ForumComment', backref='author', lazy=True)
    mentorship_mentor = db.relationship('MentorshipProgram', backref='mentor', foreign_keys='MentorshipProgram.mentor_id', lazy=True)
    mentorship_mentee = db.relationship('MentorshipProgram', backref='mentee', foreign_keys='MentorshipProgram.mentee_id', lazy=True)

class Event(db.Model):
    """Event model."""
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(100), nullable=False)
    description = db.Column(db.Text, nullable=False)
    location = db.Column(db.String(100), nullable=False)
    event_date = db.Column(db.DateTime, nullable=False)
    image = db.Column(db.String(100))
    creator_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Relationships
    creator = db.relationship('User', foreign_keys=[creator_id], backref='created_events')
    registrations = db.relationship('EventRegistration', back_populates='event', lazy=True, cascade='all, delete-orphan')

class EventRegistration(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    event_id = db.Column(db.Integer, db.ForeignKey('event.id'), nullable=False)
    registration_date = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Relationships
    user = db.relationship('User', back_populates='events')
    event = db.relationship('Event', back_populates='registrations')

class JobPost(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(100), nullable=False)
    company = db.Column(db.String(100), nullable=False)
    location = db.Column(db.String(100))
    description = db.Column(db.Text, nullable=False)
    requirements = db.Column(db.Text)
    application_link = db.Column(db.String(200))
    posted_date = db.Column(db.DateTime, default=datetime.utcnow)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)

class ForumCategory(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50), nullable=False)
    description = db.Column(db.String(200))
    
    # Relationships
    posts = db.relationship('ForumPost', backref='category', lazy=True)

class ForumPost(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(100), nullable=False)
    content = db.Column(db.Text, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    category_id = db.Column(db.Integer, db.ForeignKey('forum_category.id'), nullable=False)
    
    # Relationships
    comments = db.relationship('ForumComment', backref='post', lazy=True)

class ForumComment(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    content = db.Column(db.Text, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    post_id = db.Column(db.Integer, db.ForeignKey('forum_post.id'), nullable=False)

class MentorshipProgram(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    mentor_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    mentee_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    status = db.Column(db.String(20), default='pending')  # pending, active, completed
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    focus_area = db.Column(db.String(100))
    notes = db.Column(db.Text) 

class Chat(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    description = db.Column(db.Text)
    is_group = db.Column(db.Boolean, default=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    created_by = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    
    # Relationships
    messages = db.relationship('ChatMessage', backref='chat', lazy=True, cascade='all, delete-orphan')
    participants = db.relationship('User', secondary='chat_participants', backref='chats')
    
class ChatMessage(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    content = db.Column(db.Text, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    chat_id = db.Column(db.Integer, db.ForeignKey('chat.id'), nullable=False)
    
    # Relationship to access the sender
    sender = db.relationship('User', backref='sent_messages')

# Association table for chat participants
chat_participants = db.Table('chat_participants',
    db.Column('user_id', db.Integer, db.ForeignKey('user.id'), primary_key=True),
    db.Column('chat_id', db.Integer, db.ForeignKey('chat.id'), primary_key=True),
    db.Column('joined_at', db.DateTime, default=datetime.utcnow)
) 