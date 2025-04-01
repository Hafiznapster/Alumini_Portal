from datetime import datetime
from extensions import db

class Story(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(200), nullable=False)
    content = db.Column(db.Text, nullable=False)
    summary = db.Column(db.String(500), nullable=False)
    image = db.Column(db.String(200))  # Path to story cover image
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    author_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    status = db.Column(db.String(20), default='published')  # published, draft, archived
    views = db.Column(db.Integer, default=0)
    
    # Relationships
    author = db.relationship('User', backref=db.backref('stories', lazy='dynamic'))
    
    def __repr__(self):
        return f'<Story {self.title}>'
    
    def to_dict(self):
        return {
            'id': self.id,
            'title': self.title,
            'summary': self.summary,
            'content': self.content,
            'image': self.image,
            'created_at': self.created_at,
            'updated_at': self.updated_at,
            'author': {
                'id': self.author.id,
                'name': self.author.name,
                'profile_pic': self.author.profile_pic
            },
            'views': self.views,
            'status': self.status
        } 