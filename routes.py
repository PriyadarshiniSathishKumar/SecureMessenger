from flask import Blueprint, render_template, request, redirect, url_for, flash, jsonify, session
from flask_login import login_user, logout_user, login_required, current_user
from werkzeug.security import generate_password_hash
from models import User, Room, Message, RoomMember
from app import db
from crypto_utils import crypto_manager, CryptoError
import logging

logger = logging.getLogger(__name__)

main = Blueprint('main', __name__)

@main.route('/')
def index():
    """Home page - redirect to login if not authenticated, otherwise show chat rooms"""
    if current_user.is_authenticated:
        return redirect(url_for('main.chat'))
    return render_template('index.html')

@main.route('/register', methods=['GET', 'POST'])
def register():
    """User registration"""
    if current_user.is_authenticated:
        return redirect(url_for('main.chat'))
    
    if request.method == 'POST':
        username = request.form.get('username', '').strip()
        email = request.form.get('email', '').strip()
        password = request.form.get('password', '')
        confirm_password = request.form.get('confirm_password', '')
        
        # Validation
        if not username or not email or not password:
            flash('All fields are required.', 'error')
            return render_template('register.html')
        
        if len(username) < 3:
            flash('Username must be at least 3 characters long.', 'error')
            return render_template('register.html')
        
        if len(password) < 6:
            flash('Password must be at least 6 characters long.', 'error')
            return render_template('register.html')
        
        if password != confirm_password:
            flash('Passwords do not match.', 'error')
            return render_template('register.html')
        
        # Check if user already exists
        if User.query.filter_by(username=username).first():
            flash('Username already exists.', 'error')
            return render_template('register.html')
        
        if User.query.filter_by(email=email).first():
            flash('Email already registered.', 'error')
            return render_template('register.html')
        
        try:
            # Create new user
            user = User(username=username, email=email)
            user.set_password(password)
            
            db.session.add(user)
            db.session.commit()
            
            # Create default "General" room if it doesn't exist and add user
            general_room = Room.query.filter_by(name='General').first()
            if not general_room:
                general_room = Room(name='General', description='General chat room', created_by_id=user.id)
                db.session.add(general_room)
                db.session.commit()
            
            # Add user to general room
            general_room.add_member(user)
            db.session.commit()
            
            flash('Registration successful! Please log in.', 'success')
            return redirect(url_for('main.login'))
            
        except Exception as e:
            db.session.rollback()
            logger.error(f"Registration error: {e}")
            flash('Registration failed. Please try again.', 'error')
            return render_template('register.html')
    
    return render_template('register.html')

@main.route('/login', methods=['GET', 'POST'])
def login():
    """User login"""
    if current_user.is_authenticated:
        return redirect(url_for('main.chat'))
    
    if request.method == 'POST':
        username = request.form.get('username', '').strip()
        password = request.form.get('password', '')
        remember_me = request.form.get('remember_me') == 'on'
        
        if not username or not password:
            flash('Username and password are required.', 'error')
            return render_template('login.html')
        
        user = User.query.filter_by(username=username).first()
        
        if user and user.check_password(password):
            login_user(user, remember=remember_me)
            user.is_online = True
            db.session.commit()
            
            next_page = request.args.get('next')
            if next_page:
                return redirect(next_page)
            return redirect(url_for('main.chat'))
        else:
            flash('Invalid username or password.', 'error')
    
    return render_template('login.html')

@main.route('/logout')
@login_required
def logout():
    """User logout"""
    current_user.is_online = False
    db.session.commit()
    logout_user()
    flash('You have been logged out.', 'info')
    return redirect(url_for('main.index'))

@main.route('/chat')
@main.route('/chat/<int:room_id>')
@login_required
def chat(room_id=None):
    """Main chat interface"""
    # Get user's rooms
    user_rooms = current_user.get_rooms()
    
    if not user_rooms:
        flash('You are not a member of any rooms.', 'info')
        return redirect(url_for('main.index'))
    
    # Select room
    if room_id:
        current_room = Room.query.get_or_404(room_id)
        if not current_room.is_member(current_user):
            flash('You are not a member of this room.', 'error')
            return redirect(url_for('main.chat'))
    else:
        current_room = user_rooms[0]  # Default to first room
    
    # Get room messages
    try:
        messages = []
        raw_messages = current_room.messages.order_by(Message.timestamp.asc()).limit(50).all()
        
        for msg in raw_messages:
            try:
                decrypted_content = crypto_manager.decrypt_message(msg.content_encrypted)
                messages.append({
                    'id': msg.id,
                    'content': decrypted_content,
                    'sender': msg.sender.username,
                    'timestamp': msg.timestamp,
                    'is_own': msg.sender_id == current_user.id
                })
            except CryptoError as e:
                logger.error(f"Failed to decrypt message {msg.id}: {e}")
                messages.append({
                    'id': msg.id,
                    'content': '[Message could not be decrypted]',
                    'sender': msg.sender.username,
                    'timestamp': msg.timestamp,
                    'is_own': msg.sender_id == current_user.id
                })
        
        return render_template('chat.html', 
                             rooms=user_rooms, 
                             current_room=current_room, 
                             messages=messages)
                             
    except Exception as e:
        logger.error(f"Error loading chat: {e}")
        flash('Error loading chat messages.', 'error')
        return redirect(url_for('main.index'))

@main.route('/send_message', methods=['POST'])
@login_required
def send_message():
    """Send a new message"""
    try:
        room_id = request.form.get('room_id')
        message_content = request.form.get('message', '').strip()
        
        if not room_id or not message_content:
            flash('Room and message content are required.', 'error')
            return redirect(url_for('main.chat'))
        
        room = Room.query.get_or_404(room_id)
        
        # Check if user is member of room
        if not room.is_member(current_user):
            flash('You are not a member of this room.', 'error')
            return redirect(url_for('main.chat'))
        
        # Encrypt message
        encrypted_content = crypto_manager.encrypt_message(message_content)
        
        # Create message
        message = Message(
            content_encrypted=encrypted_content,
            sender_id=current_user.id,
            room_id=room.id
        )
        
        db.session.add(message)
        db.session.commit()
        
        logger.info(f"Message sent by {current_user.username} to room {room.name}")
        return redirect(url_for('main.chat', room_id=room.id))
        
    except CryptoError as e:
        logger.error(f"Encryption error: {e}")
        flash('Failed to encrypt message. Please try again.', 'error')
        return redirect(url_for('main.chat'))
    except Exception as e:
        logger.error(f"Error sending message: {e}")
        db.session.rollback()
        flash('Failed to send message. Please try again.', 'error')
        return redirect(url_for('main.chat'))

@main.route('/create_room', methods=['POST'])
@login_required
def create_room():
    """Create a new chat room"""
    try:
        room_name = request.form.get('room_name', '').strip()
        room_description = request.form.get('room_description', '').strip()
        
        if not room_name:
            flash('Room name is required.', 'error')
            return redirect(url_for('main.chat'))
        
        if len(room_name) < 3:
            flash('Room name must be at least 3 characters long.', 'error')
            return redirect(url_for('main.chat'))
        
        # Check if room name exists
        existing_room = Room.query.filter_by(name=room_name).first()
        if existing_room:
            flash('Room name already exists.', 'error')
            return redirect(url_for('main.chat'))
        
        # Create room
        room = Room(
            name=room_name,
            description=room_description,
            created_by_id=current_user.id
        )
        
        db.session.add(room)
        db.session.flush()  # Get room.id
        
        # Add creator as member
        room.add_member(current_user)
        db.session.commit()
        
        flash(f'Room "{room_name}" created successfully!', 'success')
        return redirect(url_for('main.chat', room_id=room.id))
        
    except Exception as e:
        logger.error(f"Error creating room: {e}")
        db.session.rollback()
        flash('Failed to create room. Please try again.', 'error')
        return redirect(url_for('main.chat'))

@main.route('/join_room', methods=['POST'])
@login_required
def join_room():
    """Join an existing room"""
    try:
        room_name = request.form.get('room_name', '').strip()
        
        if not room_name:
            flash('Room name is required.', 'error')
            return redirect(url_for('main.chat'))
        
        room = Room.query.filter_by(name=room_name).first()
        if not room:
            flash('Room not found.', 'error')
            return redirect(url_for('main.chat'))
        
        if room.is_member(current_user):
            flash('You are already a member of this room.', 'info')
            return redirect(url_for('main.chat', room_id=room.id))
        
        # Add user to room
        room.add_member(current_user)
        db.session.commit()
        
        flash(f'Successfully joined room "{room_name}"!', 'success')
        return redirect(url_for('main.chat', room_id=room.id))
        
    except Exception as e:
        logger.error(f"Error joining room: {e}")
        db.session.rollback()
        flash('Failed to join room. Please try again.', 'error')
        return redirect(url_for('main.chat'))

@main.route('/api/messages/<int:room_id>')
@login_required
def get_messages(room_id):
    """API endpoint to get recent messages for a room"""
    try:
        room = Room.query.get_or_404(room_id)
        
        if not room.is_member(current_user):
            return jsonify({'error': 'Access denied'}), 403
        
        # Get recent messages
        messages = []
        raw_messages = room.messages.order_by(Message.timestamp.desc()).limit(20).all()
        
        for msg in reversed(raw_messages):
            try:
                decrypted_content = crypto_manager.decrypt_message(msg.content_encrypted)
                messages.append({
                    'id': msg.id,
                    'content': decrypted_content,
                    'sender': msg.sender.username,
                    'timestamp': msg.timestamp.isoformat(),
                    'is_own': msg.sender_id == current_user.id
                })
            except CryptoError as e:
                logger.error(f"Failed to decrypt message {msg.id}: {e}")
                messages.append({
                    'id': msg.id,
                    'content': '[Message could not be decrypted]',
                    'sender': msg.sender.username,
                    'timestamp': msg.timestamp.isoformat(),
                    'is_own': msg.sender_id == current_user.id
                })
        
        return jsonify({'messages': messages})
        
    except Exception as e:
        logger.error(f"Error getting messages: {e}")
        return jsonify({'error': 'Failed to load messages'}), 500
