from flask import Blueprint, render_template, redirect, url_for, request, flash, jsonify
from flask_login import login_required, current_user
from models import User, Chat, ChatMessage
from datetime import datetime
from extensions import db

chat = Blueprint('chat', __name__, url_prefix='/chat')

@chat.route('/')
@login_required
def index():
    """View all chats for the current user."""
    user_chats = current_user.chats
    users = User.query.filter(User.id != current_user.id).all()
    return render_template('chat/index.html', chats=user_chats, users=users, ChatMessage=ChatMessage)

@chat.route('/create', methods=['POST'])
@login_required
def create_chat():
    """Create a new chat."""
    user_id = request.form.get('user_ids')
    first_message = request.form.get('first_message')
    
    if not user_id:
        flash('Please select a user to chat with.', 'error')
        return redirect(url_for('chat.index'))
    
    # Get the other user
    other_user = User.query.get_or_404(int(user_id))
    
    # Check if a chat already exists between these users
    existing_chat = Chat.query.filter(
        Chat.participants.contains(current_user),
        Chat.participants.contains(other_user),
        Chat.is_group_chat == False
    ).first()
    
    if existing_chat:
        # If there's a first message, add it to the existing chat
        if first_message:
            new_message = ChatMessage(
                content=first_message,
                chat_id=existing_chat.id,
                sender_id=current_user.id
            )
            db.session.add(new_message)
            db.session.commit()
        
        return redirect(url_for('chat.view', chat_id=existing_chat.id))
    
    # Create new chat
    new_chat = Chat(
        is_group_chat=False
    )
    
    # Set created_by after creation
    new_chat.created_by = current_user.id
    
    # Add participants
    new_chat.participants.append(current_user)
    new_chat.participants.append(other_user)
    
    # Set the chat name after adding participants
    new_chat.name = f"Chat with {other_user.name}"
    
    db.session.add(new_chat)
    db.session.commit()
    
    # Add first message if provided
    if first_message:
        new_message = ChatMessage(
            content=first_message,
            chat_id=new_chat.id,
            sender_id=current_user.id
        )
        db.session.add(new_message)
        db.session.commit()
    
    return redirect(url_for('chat.view', chat_id=new_chat.id))

@chat.route('/view/<int:chat_id>')
@login_required
def view(chat_id):
    """View a specific chat."""
    chat = Chat.query.get_or_404(chat_id)
    
    # Check if user is a participant
    if current_user not in chat.participants:
        flash('You are not a participant in this chat.')
        return redirect(url_for('chat.index'))
    
    messages = ChatMessage.query.filter_by(chat_id=chat_id).order_by(ChatMessage.created_at).all()
    return render_template('chat/view.html', chat=chat, messages=messages)

@chat.route('/send/<int:chat_id>', methods=['POST'])
@login_required
def send_message(chat_id):
    """Send a message in a chat."""
    chat = Chat.query.get_or_404(chat_id)
    
    # Check if user is a participant
    if current_user not in chat.participants:
        flash('You are not a participant in this chat.')
        return redirect(url_for('chat.index'))
    
    content = request.form.get('content')
    if content:
        from extensions import db
        message = ChatMessage(
            content=content,
            sender_id=current_user.id,
            chat_id=chat_id
        )
        db.session.add(message)
        db.session.commit()
    
    if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        return jsonify({
            'status': 'success',
            'message': {
                'id': message.id,
                'content': message.content,
                'user_id': message.sender_id,
                'created_at': message.created_at.isoformat(),
                'user_name': current_user.name
            }
        })
    
    return redirect(url_for('chat.view', chat_id=chat_id))

@chat.route('/messages/<int:chat_id>', methods=['GET'])
@login_required
def get_messages(chat_id):
    """Get messages for a chat (for AJAX refresh)."""
    chat = Chat.query.get_or_404(chat_id)
    
    # Check if user is a participant
    if current_user not in chat.participants:
        return jsonify({'status': 'error', 'message': 'Not authorized'})
    
    # Get the timestamp of the last message received by the client
    last_message_time = request.args.get('last_time')
    
    # If a timestamp is provided, get messages after that time
    if last_message_time:
        try:
            last_time = datetime.fromisoformat(last_message_time)
            messages = ChatMessage.query.filter(
                ChatMessage.chat_id == chat_id,
                ChatMessage.created_at > last_time
            ).order_by(ChatMessage.created_at).all()
        except ValueError:
            messages = ChatMessage.query.filter_by(chat_id=chat_id).order_by(ChatMessage.created_at).all()
    else:
        # Get all messages if no timestamp provided
        messages = ChatMessage.query.filter_by(chat_id=chat_id).order_by(ChatMessage.created_at).all()
    
    message_list = []
    for message in messages:
        message_list.append({
            'id': message.id,
            'content': message.content,
            'user_id': message.sender_id,
            'created_at': message.created_at.isoformat(),
            'user_name': message.sender.name
        })
    
    return jsonify({'status': 'success', 'messages': message_list})

@chat.route('/add-participant/<int:chat_id>', methods=['POST'])
@login_required
def add_participant(chat_id):
    """Add a participant to a chat."""
    chat = Chat.query.get_or_404(chat_id)
    
    # Check if user is the creator or an admin
    if chat.created_by != current_user.id and not current_user.is_admin:
        flash('You do not have permission to add participants to this chat.')
        return redirect(url_for('chat.view', chat_id=chat_id))
    
    user_id = request.form.get('user_id')
    if user_id:
        user = User.query.get(int(user_id))
        if user and user not in chat.participants:
            from extensions import db
            chat.participants.append(user)
            db.session.commit()
            flash(f'{user.name} has been added to the chat.')
    
    return redirect(url_for('chat.view', chat_id=chat_id))

@chat.route('/leave/<int:chat_id>')
@login_required
def leave_chat(chat_id):
    """Leave a chat."""
    chat = Chat.query.get_or_404(chat_id)
    
    if current_user in chat.participants:
        from extensions import db
        chat.participants.remove(current_user)
        
        # If no participants left, delete the chat
        if not chat.participants:
            db.session.delete(chat)
        
        db.session.commit()
        flash('You have left the chat.')
    
    return redirect(url_for('chat.index'))






