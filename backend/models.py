from datetime import datetime
from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()

class Job(db.Model):
    __tablename__ = 'jobs'
    
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(200), nullable=False)
    company = db.Column(db.String(100), nullable=False)
    location = db.Column(db.String(100), nullable=False)
    salary = db.Column(db.String(50), default='Negotiable')
    job_type = db.Column(db.String(20), default='Full-time')  # Full-time, Part-time, Remote, Contract
    category = db.Column(db.String(50), default='IT')
    description = db.Column(db.Text, nullable=False)
    requirements = db.Column(db.Text)
    benefits = db.Column(db.Text)
    posted_date = db.Column(db.DateTime, default=datetime.utcnow)
    is_active = db.Column(db.Boolean, default=True)
    
    # Relationship with applications
    applications = db.relationship('Application', backref='job', lazy=True, cascade='all, delete-orphan')
    
    def to_dict(self):
        return {
            'id': self.id,
            'title': self.title,
            'company': self.company,
            'location': self.location,
            'salary': self.salary,
            'job_type': self.job_type,
            'category': self.category,
            'description': self.description,
            'requirements': self.requirements,
            'benefits': self.benefits,
            'posted_date': self.posted_date.isoformat() if self.posted_date else None,
            'is_active': self.is_active,
            'application_count': len(self.applications)
        }

class Application(db.Model):
    __tablename__ = 'applications'
    
    id = db.Column(db.Integer, primary_key=True)
    job_id = db.Column(db.Integer, db.ForeignKey('jobs.id', ondelete='CASCADE'), nullable=False)
    name = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(100), nullable=False)
    phone = db.Column(db.String(20), nullable=False)
    resume_url = db.Column(db.String(500))
    cover_letter = db.Column(db.Text)
    experience = db.Column(db.Integer, default=0)
    skills = db.Column(db.String(500))
    applied_date = db.Column(db.DateTime, default=datetime.utcnow)
    status = db.Column(db.String(20), default='Pending')  # Pending, Reviewed, Shortlisted, Rejected
    
    def to_dict(self):
        return {
            'id': self.id,
            'job_id': self.job_id,
            'name': self.name,
            'email': self.email,
            'phone': self.phone,
            'resume_url': self.resume_url,
            'cover_letter': self.cover_letter,
            'experience': self.experience,
            'skills': self.skills,
            'applied_date': self.applied_date.isoformat() if self.applied_date else None,
            'status': self.status
        }