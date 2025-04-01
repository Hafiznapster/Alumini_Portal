from flask import Blueprint, render_template, request, flash, redirect, url_for, jsonify
from flask_login import login_required, current_user
from models import User, Mentor, MentorshipRelation
from extensions import db
from datetime import datetime

bp = Blueprint('mentorship', __name__)

@bp.route('/mentorship')
@login_required
def index():
    # For alumni: show their mentor profile and mentee requests
    # For users: show available mentors and their mentorship status
    if current_user.role == 'alumni':
        mentor = Mentor.query.filter_by(user_id=current_user.id).first()
        if mentor:
            mentorship_requests = MentorshipRelation.query.filter_by(mentor_id=mentor.id).all()
            return render_template('mentorship/mentor_dashboard.html', mentor=mentor, mentorship_requests=mentorship_requests)
        return render_template('mentorship/become_mentor.html')
    else:
        # For users, show available mentors and their current mentorship status
        available_mentors = Mentor.query.filter_by(is_available=True).all()
        my_mentorships = MentorshipRelation.query.filter_by(mentee_id=current_user.id).all()
        return render_template('mentorship/mentee_dashboard.html', mentors=available_mentors, my_mentorships=my_mentorships)

@bp.route('/mentorship/register', methods=['GET', 'POST'])
@login_required
def register_mentor():
    if current_user.role != 'alumni':
        flash('Only alumni can register as mentors.', 'error')
        return redirect(url_for('mentorship.index'))
    
    if request.method == 'POST':
        expertise = request.form.get('expertise')
        bio = request.form.get('bio')
        availability = request.form.get('availability')
        is_available = request.form.get('is_available', 'true').lower() == 'true'
        
        if not all([expertise, bio, availability]):
            flash('All fields are required.', 'error')
            return redirect(url_for('mentorship.register_mentor'))
        
        mentor = Mentor(
            user_id=current_user.id,
            expertise=expertise,
            bio=bio,
            availability=availability,
            is_available=is_available
        )
        db.session.add(mentor)
        db.session.commit()
        
        flash('Successfully registered as a mentor!', 'success')
        return redirect(url_for('mentorship.index'))
    
    return render_template('mentorship/register.html')

@bp.route('/mentorship/request/<int:mentor_id>', methods=['POST'])
@login_required
def request_mentor(mentor_id):
    if current_user.role != 'user':
        flash('Only users can request mentors.', 'error')
        return redirect(url_for('mentorship.index'))
    
    # Check if already requested or has active mentorship
    existing_request = MentorshipRelation.query.filter_by(
        mentee_id=current_user.id,
        mentor_id=mentor_id
    ).first()
    
    if existing_request:
        flash('You have already requested or are in a mentorship with this mentor.', 'info')
        return redirect(url_for('mentorship.index'))
    
    mentor = Mentor.query.get_or_404(mentor_id)
    if not mentor.is_available:
        flash('This mentor is currently not available for mentorship.', 'error')
        return redirect(url_for('mentorship.index'))
    
    mentorship = MentorshipRelation(
        mentor_id=mentor_id,
        mentee_id=current_user.id
    )
    db.session.add(mentorship)
    db.session.commit()
    
    flash('Mentorship request sent successfully!', 'success')
    return redirect(url_for('mentorship.index'))

@bp.route('/mentorship/respond/<int:request_id>/<string:action>')
@login_required
def respond_to_request(request_id, action):
    if current_user.role != 'alumni':
        flash('Only alumni can respond to mentorship requests.', 'error')
        return redirect(url_for('mentorship.index'))
    
    mentorship = MentorshipRelation.query.get_or_404(request_id)
    mentor = Mentor.query.filter_by(user_id=current_user.id).first()
    
    if not mentor or mentorship.mentor_id != mentor.id:
        flash('You are not authorized to respond to this request.', 'error')
        return redirect(url_for('mentorship.index'))
    
    if action == 'accept':
        mentorship.status = 'accepted'
        mentorship.accepted_at = datetime.utcnow()
        flash('You have accepted the mentorship request.', 'success')
    elif action == 'reject':
        mentorship.status = 'rejected'
        flash('You have rejected the mentorship request.', 'info')
    
    db.session.commit()
    return redirect(url_for('mentorship.index'))

@bp.route('/mentorship/toggle-availability', methods=['POST'])
@login_required
def toggle_availability():
    """Toggle mentor availability status."""
    if current_user.role != 'alumni':
        return jsonify({'error': 'Only alumni can toggle availability'}), 403
    
    mentor = Mentor.query.filter_by(user_id=current_user.id).first()
    if not mentor:
        return jsonify({'error': 'Mentor profile not found'}), 404
    
    mentor.is_available = not mentor.is_available
    db.session.commit()
    
    return jsonify({
        'success': True,
        'is_available': mentor.is_available
    }) 
