from datetime import datetime
from extensions import db

class Mentor(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), unique=True, nullable=False)
    bio = db.Column(db.Text)
    expertise = db.Column(db.String(200))
    availability = db.Column(db.Text)
    is_available = db.Column(db.Boolean, default=True)  # Whether the mentor is currently accepting new mentees
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Relationships
    user = db.relationship('User', backref=db.backref('mentor_profile', uselist=False))
    mentorship_relations = db.relationship('MentorshipRelation', backref='mentor', lazy='dynamic')

class MentorshipRelation(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    mentor_id = db.Column(db.Integer, db.ForeignKey('mentor.id'), nullable=False)
    mentee_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    status = db.Column(db.String(20), default='pending')  # pending, accepted, rejected
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Relationship with mentee
    mentee = db.relationship('User', backref='mentorship_requests') 