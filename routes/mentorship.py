from flask import Blueprint, render_template, redirect, url_for, request, flash
from flask_login import login_required, current_user
from models import User, MentorshipProgram
from extensions import db

mentorship = Blueprint('mentorship', __name__, url_prefix='/mentorship')

@mentorship.route('/')
@login_required
def index():
    """View mentorship dashboard."""
    mentor_programs = MentorshipProgram.query.filter_by(mentor_id=current_user.id).all()
    mentee_programs = MentorshipProgram.query.filter_by(mentee_id=current_user.id).all()
    return render_template('mentorship/index.html', 
                          mentor_programs=mentor_programs, 
                          mentee_programs=mentee_programs)

@mentorship.route('/become-mentor', methods=['GET', 'POST'])
@login_required
def become_mentor():
    """Register as a mentor."""
    if request.method == 'POST':
        # Update user profile with mentor information
        current_user.mentor_status = True
        current_user.mentor_fields = request.form.get('fields')
        current_user.mentor_bio = request.form.get('mentor_bio')
        
        db.session.commit()
        
        flash('You are now registered as a mentor!')
        return redirect(url_for('mentorship.index'))
        
    return render_template('mentorship/become_mentor.html')

@mentorship.route('/mentors')
@login_required
def mentor_list():
    """View list of available mentors."""
    mentors = User.query.filter_by(mentor_status=True).all()
    return render_template('mentorship/mentor_list.html', mentors=mentors)

@mentorship.route('/request/<int:mentor_id>', methods=['GET', 'POST'])
@login_required
def request_mentorship(mentor_id):
    """Request mentorship from a specific mentor."""
    mentor = User.query.get_or_404(mentor_id)
    
    # Check if already in a mentorship with this mentor
    existing = MentorshipProgram.query.filter_by(mentor_id=mentor_id, mentee_id=current_user.id).first()
    if existing:
        flash('You already have a mentorship program with this mentor.')
        return redirect(url_for('mentorship.mentor_list'))
        
    if request.method == 'POST':
        focus_area = request.form.get('focus_area')
        notes = request.form.get('notes')
        
        new_program = MentorshipProgram(
            mentor_id=mentor_id,
            mentee_id=current_user.id,
            focus_area=focus_area,
            notes=notes
        )
        
        db.session.add(new_program)
        db.session.commit()
        
        flash('Mentorship request sent successfully!')
        return redirect(url_for('mentorship.index'))
        
    return render_template('mentorship/request.html', mentor=mentor)

@mentorship.route('/respond/<int:program_id>/<string:action>')
@login_required
def respond_to_request(program_id, action):
    """Respond to a mentorship request (accept/decline)."""
    program = MentorshipProgram.query.get_or_404(program_id)
    
    # Check if user is the mentor
    if program.mentor_id != current_user.id:
        flash('You do not have permission to respond to this request.')
        return redirect(url_for('mentorship.index'))
        
    if action == 'accept':
        program.status = 'active'
        flash('You have accepted the mentorship request.')
    elif action == 'decline':
        program.status = 'declined'
        flash('You have declined the mentorship request.')
    
    db.session.commit()
    return redirect(url_for('mentorship.index'))

@mentorship.route('/complete/<int:program_id>')
@login_required
def complete_mentorship(program_id):
    """Mark a mentorship program as completed."""
    program = MentorshipProgram.query.get_or_404(program_id)
    
    # Check if user is involved in the program
    if program.mentor_id != current_user.id and program.mentee_id != current_user.id:
        flash('You do not have permission to update this program.')
        return redirect(url_for('mentorship.index'))
        
    program.status = 'completed'
    db.session.commit()
    
    flash('Mentorship program marked as completed.')
    return redirect(url_for('mentorship.index')) 
