from flask import Blueprint, render_template, redirect, url_for, request, flash
from flask_login import login_required, current_user
from models import Event, EventRegistration
from datetime import datetime
from werkzeug.utils import secure_filename
import os

events = Blueprint('events', __name__, url_prefix='/events')

@events.route('/')
@login_required
def index():
    """View all events."""
    upcoming_events = Event.query.filter(Event.event_date >= datetime.utcnow()).order_by(Event.event_date).all()
    past_events = Event.query.filter(Event.event_date < datetime.utcnow()).order_by(Event.event_date.desc()).all()
    return render_template('events/index.html', upcoming_events=upcoming_events, past_events=past_events)

@events.route('/view/<int:event_id>')
def view_event(event_id):
    """View details of a specific event."""
    event = Event.query.get_or_404(event_id)
    registered = False
    if current_user.is_authenticated:
        registration = EventRegistration.query.filter_by(user_id=current_user.id, event_id=event_id).first()
        registered = registration is not None
    return render_template('events/view.html', event=event, registered=registered)

@events.route('/register/<int:event_id>')
@login_required
def register_event(event_id):
    """Register for an event."""
    event = Event.query.get_or_404(event_id)
    
    # Check if already registered
    registration = EventRegistration.query.filter_by(user_id=current_user.id, event_id=event_id).first()
    if registration:
        flash('You are already registered for this event.')
        return redirect(url_for('events.view_event', event_id=event_id))
        
    # Check if event date has passed
    if event.event_date < datetime.utcnow():
        flash('This event has already taken place.')
        return redirect(url_for('events.view_event', event_id=event_id))
        
    # Register for the event
    from app import db
    registration = EventRegistration(user_id=current_user.id, event_id=event_id)
    db.session.add(registration)
    db.session.commit()
    
    flash('You have successfully registered for this event!')
    return redirect(url_for('events.view_event', event_id=event_id))

@events.route('/unregister/<int:event_id>')
@login_required
def unregister_event(event_id):
    """Unregister from an event."""
    event = Event.query.get_or_404(event_id)
    
    # Check if already registered
    registration = EventRegistration.query.filter_by(user_id=current_user.id, event_id=event_id).first()
    if not registration:
        flash('You are not registered for this event.')
        return redirect(url_for('events.view_event', event_id=event_id))
        
    # Check if event date has passed
    if event.event_date < datetime.utcnow():
        flash('This event has already taken place.')
        return redirect(url_for('events.view_event', event_id=event_id))
        
    # Unregister from the event
    from app import db
    db.session.delete(registration)
    db.session.commit()
    
    flash('You have successfully unregistered from this event.')
    return redirect(url_for('events.view_event', event_id=event_id))

@events.route('/my-events')
@login_required
def my_events():
    """View events the user is registered for."""
    registrations = EventRegistration.query.filter_by(user_id=current_user.id).all()
    events = [reg.event for reg in registrations]
    upcoming = [event for event in events if event.event_date >= datetime.utcnow()]
    past = [event for event in events if event.event_date < datetime.utcnow()]
    return render_template('events/my_events.html', upcoming_events=upcoming, past_events=past)

@events.route('/create', methods=['GET', 'POST'])
@login_required
def create_event():
    """Create a new event (admin only)."""
    if not current_user.is_admin:
        flash('You do not have permission to create events.')
        return redirect(url_for('events.index'))
        
    if request.method == 'POST':
        title = request.form.get('title')
        description = request.form.get('description')
        location = request.form.get('location')
        event_date_str = request.form.get('event_date')
        event_time_str = request.form.get('event_time')
        
        # Parse date and time
        event_datetime = datetime.strptime(f"{event_date_str} {event_time_str}", "%Y-%m-%d %H:%M")
        
        # Handle image upload
        image = None
        if 'image' in request.files:
            file = request.files['image']
            if file.filename:
                filename = secure_filename(file.filename)
                file_path = os.path.join('static/images/events', filename)
                file.save(file_path)
                image = filename
        
        new_event = Event(
            title=title,
            description=description,
            location=location,
            event_date=event_datetime,
            image=image
        )
        
        from app import db
        db.session.add(new_event)
        db.session.commit()
        
        flash('Event created successfully!')
        return redirect(url_for('events.view_event', event_id=new_event.id))
        
    return render_template('events/create.html')