import os
from flask import Flask, request, jsonify, send_from_directory
from flask_cors import CORS
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime

app = Flask(__name__, static_folder='../frontend', static_url_path='')
CORS(app)

# Database Setup
app.config['SQLALCHEMY_DATABASE_URI'] = os.environ.get('DATABASE_URL', 'sqlite:///jobs.db')
if app.config['SQLALCHEMY_DATABASE_URI'] and app.config['SQLALCHEMY_DATABASE_URI'].startswith('postgres://'):
    app.config['SQLALCHEMY_DATABASE_URI'] = app.config['SQLALCHEMY_DATABASE_URI'].replace('postgres://', 'postgresql://', 1)
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['ADMIN_PASSWORD'] = os.environ.get('ADMIN_PASSWORD', 'njp123')

db = SQLAlchemy(app)

# Database Models
class Job(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(200), nullable=False)
    company = db.Column(db.String(100), nullable=False)
    location = db.Column(db.String(100), nullable=False)
    salary = db.Column(db.String(50), default='Negotiable')
    job_type = db.Column(db.String(20), default='Full-time')
    category = db.Column(db.String(50), default='Other')
    description = db.Column(db.Text, nullable=False)
    requirements = db.Column(db.Text)
    benefits = db.Column(db.Text)
    posted_date = db.Column(db.DateTime, default=datetime.utcnow)
    is_active = db.Column(db.Boolean, default=True)

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
            'application_count': Application.query.filter_by(job_id=self.id).count()
        }

class Application(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    job_id = db.Column(db.Integer, db.ForeignKey('job.id'), nullable=False)
    name = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(100), nullable=False)
    phone = db.Column(db.String(20), nullable=False)
    resume_url = db.Column(db.String(500))
    cover_letter = db.Column(db.Text)
    experience = db.Column(db.Integer, default=0)
    skills = db.Column(db.String(500))
    applied_date = db.Column(db.DateTime, default=datetime.utcnow)
    status = db.Column(db.String(20), default='Pending')

# Create tables
with app.app_context():
    db.create_all()

# Helper function for admin auth
def check_admin():
    password = request.headers.get('X-Admin-Password')
    return password == app.config['ADMIN_PASSWORD']

# Routes
@app.route('/')
def home():
    return send_from_directory('frontend', 'index.html')

@app.route('/admin')
def admin_page():
    return send_from_directory('frontend', 'admin.html')

@app.route('/api/jobs', methods=['GET'])
def get_jobs():
    jobs = Job.query.filter_by(is_active=True).order_by(Job.posted_date.desc()).all()
    return jsonify([job.to_dict() for job in jobs])

@app.route('/api/jobs/all', methods=['GET'])
def get_all_jobs():
    if not check_admin():
        return jsonify({'error': 'Unauthorized'}), 401
    jobs = Job.query.order_by(Job.posted_date.desc()).all()
    return jsonify([job.to_dict() for job in jobs])

@app.route('/api/jobs', methods=['POST'])
def create_job():
    if not check_admin():
        return jsonify({'error': 'Unauthorized'}), 401
    
    data = request.get_json()
    job = Job(
        title=data['title'],
        company=data['company'],
        location=data['location'],
        salary=data.get('salary', 'Negotiable'),
        job_type=data.get('job_type', 'Full-time'),
        category=data.get('category', 'Other'),
        description=data['description'],
        requirements=data.get('requirements', ''),
        benefits=data.get('benefits', ''),
        is_active=data.get('is_active', True)
    )
    db.session.add(job)
    db.session.commit()
    return jsonify({'id': job.id, 'message': 'Job created'}), 201

@app.route('/api/jobs/<int:job_id>', methods=['PUT'])
def update_job(job_id):
    if not check_admin():
        return jsonify({'error': 'Unauthorized'}), 401
    
    job = Job.query.get_or_404(job_id)
    data = request.get_json()
    
    job.title = data.get('title', job.title)
    job.company = data.get('company', job.company)
    job.location = data.get('location', job.location)
    job.salary = data.get('salary', job.salary)
    job.job_type = data.get('job_type', job.job_type)
    job.category = data.get('category', job.category)
    job.description = data.get('description', job.description)
    job.requirements = data.get('requirements', job.requirements)
    job.benefits = data.get('benefits', job.benefits)
    job.is_active = data.get('is_active', job.is_active)
    
    db.session.commit()
    return jsonify({'message': 'Job updated'})

@app.route('/api/jobs/<int:job_id>', methods=['DELETE'])
def delete_job(job_id):
    if not check_admin():
        return jsonify({'error': 'Unauthorized'}), 401
    
    job = Job.query.get_or_404(job_id)
    db.session.delete(job)
    db.session.commit()
    return jsonify({'message': 'Job deleted'})

@app.route('/api/stats', methods=['GET'])
def get_stats():
    if not check_admin():
        return jsonify({'error': 'Unauthorized'}), 401
    
    total_jobs = Job.query.count()
    active_jobs = Job.query.filter_by(is_active=True).count()
    total_applications = Application.query.count()
    pending_applications = Application.query.filter_by(status='Pending').count()
    
    return jsonify({
        'total_jobs': total_jobs,
        'active_jobs': active_jobs,
        'total_applications': total_applications,
        'applications_by_status': {
            'pending': pending_applications
        }
    })

@app.route('/api/jobs/<int:job_id>/apply', methods=['POST'])
def apply_job(job_id):
    data = request.get_json()
    application = Application(
        job_id=job_id,
        name=data['name'],
        email=data['email'],
        phone=data['phone'],
        resume_url=data.get('resume_url', ''),
        cover_letter=data.get('cover_letter', ''),
        experience=data.get('experience', 0),
        skills=data.get('skills', '')
    )
    db.session.add(application)
    db.session.commit()
    return jsonify({'message': 'Application submitted'}), 201

@app.route('/api/applications', methods=['GET'])
def get_applications():
    if not check_admin():
        return jsonify({'error': 'Unauthorized'}), 401
    
    applications = Application.query.order_by(Application.applied_date.desc()).all()
    result = []
    for app in applications:
        result.append({
            'id': app.id,
            'job_id': app.job_id,
            'name': app.name,
            'email': app.email,
            'phone': app.phone,
            'experience': app.experience,
            'skills': app.skills,
            'status': app.status,
            'applied_date': app.applied_date.isoformat() if app.applied_date else None
        })
    return jsonify(result)

@app.route('/health')
def health():
    return jsonify({'status': 'healthy'}), 200

# Serve static files
@app.route('/<path:path>')
def serve_static(path):
    return send_from_directory('frontend', path)

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)