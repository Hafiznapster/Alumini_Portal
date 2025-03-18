from flask import Blueprint, render_template, redirect, url_for, request, flash
from flask_login import login_required, current_user
from models import JobPost
from datetime import datetime

jobs = Blueprint('jobs', __name__, url_prefix='/jobs')

@jobs.route('/')
@login_required
def index():
    """View all job opportunities."""
    job_posts = JobPost.query.order_by(JobPost.posted_date.desc()).all()
    return render_template('jobs/index.html', job_posts=job_posts)

@jobs.route('/view/<int:job_id>')
def view_job(job_id):
    """View details of a specific job posting."""
    job = JobPost.query.get_or_404(job_id)
    return render_template('jobs/view.html', job=job)

@jobs.route('/create', methods=['GET', 'POST'])
@login_required
def create_job():
    """Create a new job posting."""
    if request.method == 'POST':
        from app import db
        title = request.form.get('title')
        company = request.form.get('company')
        location = request.form.get('location')
        description = request.form.get('description')
        requirements = request.form.get('requirements')
        application_link = request.form.get('application_link')
        
        new_job = JobPost(
            title=title,
            company=company,
            location=location,
            description=description,
            requirements=requirements,
            application_link=application_link,
            user_id=current_user.id
        )
        
        db.session.add(new_job)
        db.session.commit()
        
        flash('Job posting created successfully!')
        return redirect(url_for('jobs.view_job', job_id=new_job.id))
        
    return render_template('jobs/create.html')

@jobs.route('/edit/<int:job_id>', methods=['GET', 'POST'])
@login_required
def edit_job(job_id):
    """Edit an existing job posting."""
    job = JobPost.query.get_or_404(job_id)
    
    # Check if user is the author or an admin
    if job.user_id != current_user.id and not current_user.is_admin:
        flash('You do not have permission to edit this job posting.')
        return redirect(url_for('jobs.view_job', job_id=job_id))
        
    if request.method == 'POST':
        from app import db
        job.title = request.form.get('title')
        job.company = request.form.get('company')
        job.location = request.form.get('location')
        job.description = request.form.get('description')
        job.requirements = request.form.get('requirements')
        job.application_link = request.form.get('application_link')
        
        db.session.commit()
        
        flash('Job posting updated successfully!')
        return redirect(url_for('jobs.view_job', job_id=job_id))
        
    return render_template('jobs/edit.html', job=job)

@jobs.route('/delete/<int:job_id>')
@login_required
def delete_job(job_id):
    """Delete a job posting."""
    job = JobPost.query.get_or_404(job_id)
    
    # Check if user is the author or an admin
    if job.user_id != current_user.id and not current_user.is_admin:
        flash('You do not have permission to delete this job posting.')
        return redirect(url_for('jobs.view_job', job_id=job_id))
        
    from app import db
    db.session.delete(job)
    db.session.commit()
    
    flash('Job posting deleted successfully!')
    return redirect(url_for('jobs.index'))