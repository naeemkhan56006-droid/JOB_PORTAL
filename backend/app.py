import os
import re
from flask import Flask, request, jsonify, send_from_directory
from flask_cors import CORS
from models import db, Job, Application
from config import Config
from datetime import datetime

app = Flask(__name__, static_folder='../frontend', static_url_path='')
app.config.from_object(Config)

# Initialize extensions
CORS(app)
db.init_app(app)

# Fix for Railway PostgreSQL URL
if app.config['SQLALCHEMY_DATABASE_URI']:
    if app.config['SQLALCHEMY_DATABASE_URI'].startswith('postgres://'):
        app.config['SQLALCHEMY_DATABASE_URI'] = app.config['SQLALCHEMY_DATABASE_URI'].replace(
            'postgres://', 'postgresql://', 1
        )

# Create tables
with app.app_context():
    db.create_all()

# Helper function for admin authentication
def check_admin_auth():
    admin_password = request.headers.get('X-Admin-Password')
    return admin_password == app.config['ADMIN_PASSWORD']

# Error handlers
@app.errorhandler(404)
def not_found(error):
    return jsonify({'error': 'Not found'}), 404

@app.errorhandler(500)
def internal_error(error):
    return jsonify({'error': 'Internal server error'}), 500

@app.errorhandler(400)
def bad_request(error):
    return jsonify({'error': 'Bad request'}), 400

# API Routes
@app.route('/api/jobs', methods=['GET'])
def get_jobs():
    """Get all active jobs"""
    try:
        jobs = Job.query.filter_by(is_active=True).order_by(Job.posted_date.desc()).all()
        return jsonify([job.to_dict() for job in jobs])
    except Exception as e:
        app.logger.error(f"Error fetching jobs: {str(e)}")
        return jsonify({'error': 'Failed to fetch jobs'}), 500

@app.route('/api/jobs/all', methods=['GET'])
def get_all_jobs():
    """Get all jobs (including inactive) - Admin only"""
    if not check_admin_auth():
        return jsonify({'error': 'Unauthorized'}), 401
    
    try:
        jobs = Job.query.order_by(Job.posted_date.desc()).all()
        return jsonify([job.to_dict() for job in jobs])
    except Exception as e:
        app.logger.error(f"Error fetching all jobs: {str(e)}")
        return jsonify({'error': 'Failed to fetch jobs'}), 500

@app.route('/api/jobs/<int:job_id>', methods=['GET'])
def get_job(job_id):
    """Get a specific job"""
    try:
        job = Job.query.get_or_404(job_id)
        return jsonify(job.to_dict())
    except Exception as e:
        app.logger.error(f"Error fetching job {job_id}: {str(e)}")
        return jsonify({'error': 'Job not found'}), 404

@app.route('/api/jobs', methods=['POST'])
def create_job():
    """Create a new job - Admin only"""
    if not check_admin_auth():
        return jsonify({'error': 'Unauthorized'}), 401
    
    try:
        data = request.get_json()
        
        # Validate required fields
        required_fields = ['title', 'company', 'location', 'description']
        for field in required_fields:
            if not data.get(field):
                return jsonify({'error': f'{field} is required'}), 400
        
        # Create new job
        job = Job(
            title=data['title'],
            company=data['company'],
            location=data['location'],
            salary=data.get('salary', 'Negotiable'),
            job_type=data.get('job_type', 'Full-time'),
            category=data.get('category', 'IT'),
            description=data['description'],
            requirements=data.get('requirements', ''),
            benefits=data.get('benefits', ''),
            is_active=data.get('is_active', True)
        )
        
        db.session.add(job)
        db.session.commit()
        
        return jsonify(job.to_dict()), 201
    except Exception as e:
        db.session.rollback()
        app.logger.error(f"Error creating job: {str(e)}")
        return jsonify({'error': 'Failed to create job'}), 500

@app.route('/api/jobs/<int:job_id>', methods=['PUT'])
def update_job(job_id):
    """Update a job - Admin only"""
    if not check_admin_auth():
        return jsonify({'error': 'Unauthorized'}), 401
    
    try:
        job = Job.query.get_or_404(job_id)
        data = request.get_json()
        
        # Update fields
        update_fields = ['title', 'company', 'location', 'salary', 'job_type', 
                        'category', 'description', 'requirements', 'benefits', 'is_active']
        
        for field in update_fields:
            if field in data:
                setattr(job, field, data[field])
        
        db.session.commit()
        return jsonify(job.to_dict())
    except Exception as e:
        db.session.rollback()
        app.logger.error(f"Error updating job {job_id}: {str(e)}")
        return jsonify({'error': 'Failed to update job'}), 500

@app.route('/api/jobs/<int:job_id>', methods=['DELETE'])
def delete_job(job_id):
    """Delete a job - Admin only"""
    if not check_admin_auth():
        return jsonify({'error': 'Unauthorized'}), 401
    
    try:
        job = Job.query.get_or_404(job_id)
        db.session.delete(job)
        db.session.commit()
        return jsonify({'message': 'Job deleted successfully'})
    except Exception as e:
        db.session.rollback()
        app.logger.error(f"Error deleting job {job_id}: {str(e)}")
        return jsonify({'error': 'Failed to delete job'}), 500

@app.route('/api/jobs/<int:job_id>/apply', methods=['POST'])
def apply_for_job(job_id):
    """Submit application for a job"""
    try:
        job = Job.query.get_or_404(job_id)
        
        if not job.is_active:
            return jsonify({'error': 'Job is no longer active'}), 400
        
        data = request.get_json()
        
        # Validate required fields
        required_fields = ['name', 'email', 'phone']
        for field in required_fields:
            if not data.get(field):
                return jsonify({'error': f'{field} is required'}), 400
        
        # Validate email format
        email_regex = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
        if not re.match(email_regex, data['email']):
            return jsonify({'error': 'Invalid email format'}), 400
        
        # Create application
        application = Application(
            job_id=job_id,
            name=data['name'],
            email=data['email'],
            phone=data['phone'],
            resume_url=data.get('resume_url', ''),
            cover_letter=data.get('cover_letter', ''),
            experience=data.get('experience', 0),
            skills=data.get('skills', ''),
            status='Pending'
        )
        
        db.session.add(application)
        db.session.commit()
        
        return jsonify(application.to_dict()), 201
    except Exception as e:
        db.session.rollback()
        app.logger.error(f"Error applying for job {job_id}: {str(e)}")
        return jsonify({'error': 'Failed to submit application'}), 500

@app.route('/api/applications', methods=['GET'])
def get_applications():
    """Get all applications - Admin only"""
    if not check_admin_auth():
        return jsonify({'error': 'Unauthorized'}), 401
    
    try:
        applications = Application.query.order_by(Application.applied_date.desc()).all()
        
        # Include job details with each application
        result = []
        for app in applications:
            app_dict = app.to_dict()
            job = Job.query.get(app.job_id)
            if job:
                app_dict['job_title'] = job.title
                app_dict['company'] = job.company
            result.append(app_dict)
        
        return jsonify(result)
    except Exception as e:
        app.logger.error(f"Error fetching applications: {str(e)}")
        return jsonify({'error': 'Failed to fetch applications'}), 500

@app.route('/api/applications/<int:app_id>', methods=['PUT'])
def update_application(app_id):
    """Update application status - Admin only"""
    if not check_admin_auth():
        return jsonify({'error': 'Unauthorized'}), 401
    
    try:
        application = Application.query.get_or_404(app_id)
        data = request.get_json()
        
        if 'status' in data:
            valid_statuses = ['Pending', 'Reviewed', 'Shortlisted', 'Rejected']
            if data['status'] not in valid_statuses:
                return jsonify({'error': 'Invalid status'}), 400
            application.status = data['status']
        
        db.session.commit()
        return jsonify(application.to_dict())
    except Exception as e:
        db.session.rollback()
        app.logger.error(f"Error updating application {app_id}: {str(e)}")
        return jsonify({'error': 'Failed to update application'}), 500

@app.route('/api/stats', methods=['GET'])
def get_stats():
    """Get dashboard statistics - Admin only"""
    if not check_admin_auth():
        return jsonify({'error': 'Unauthorized'}), 401
    
    try:
        total_jobs = Job.query.count()
        active_jobs = Job.query.filter_by(is_active=True).count()
        total_applications = Application.query.count()
        
        # Applications by status
        pending_apps = Application.query.filter_by(status='Pending').count()
        reviewed_apps = Application.query.filter_by(status='Reviewed').count()
        shortlisted_apps = Application.query.filter_by(status='Shortlisted').count()
        rejected_apps = Application.query.filter_by(status='Rejected').count()
        
        return jsonify({
            'total_jobs': total_jobs,
            'active_jobs': active_jobs,
            'total_applications': total_applications,
            'applications_by_status': {
                'pending': pending_apps,
                'reviewed': reviewed_apps,
                'shortlisted': shortlisted_apps,
                'rejected': rejected_apps
            }
        })
    except Exception as e:
        app.logger.error(f"Error fetching stats: {str(e)}")
        return jsonify({'error': 'Failed to fetch statistics'}), 500

# Serve frontend files
@app.route('/')
def serve_index():
    return send_from_directory(app.static_folder, 'index.html')

@app.route('/admin')
def serve_admin():
    return send_from_directory(app.static_folder, 'admin.html')

@app.route('/<path:path>')
def serve_static(path):
    return send_from_directory(app.static_folder, path)

# Health check endpoint for Railway
@app.route('/health')
def health_check():
    return jsonify({'status': 'healthy', 'database': 'connected'}), 200

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)