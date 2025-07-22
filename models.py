from app import db
from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime
import uuid

class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(64), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(256), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    is_online = db.Column(db.Boolean, default=False)
    
    # Relationships
    sent_messages = db.relationship('Message', foreign_keys='Message.sender_id', backref='sender', lazy='dynamic')
    room_memberships = db.relationship('RoomMember', backref='user', lazy='dynamic')

    def set_password(self, password):
        """Hash and set the user's password"""
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        """Check if the provided password matches the hash"""
        return check_password_hash(self.password_hash, password)

    def get_rooms(self):
        """Get all rooms the user is a member of"""
        return [membership.room for membership in self.room_memberships]

    def __repr__(self):
        return f'<User {self.username}>'

class Room(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    description = db.Column(db.Text)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    created_by_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    is_private = db.Column(db.Boolean, default=False)
    
    # Relationships
    messages = db.relationship('Message', backref='room', lazy='dynamic', cascade='all, delete-orphan')
    members = db.relationship('RoomMember', backref='room', lazy='dynamic', cascade='all, delete-orphan')
    creator = db.relationship('User', backref='created_rooms')

    def get_members(self):
        """Get all members of the room"""
        return [membership.user for membership in self.members]

    def add_member(self, user):
        """Add a user to the room"""
        if not self.is_member(user):
            membership = RoomMember(user_id=user.id, room_id=self.id)
            db.session.add(membership)
            return True
        return False

    def is_member(self, user):
        """Check if user is a member of the room"""
        return self.members.filter_by(user_id=user.id).first() is not None

    def __repr__(self):
        return f'<Room {self.name}>'

class RoomMember(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    room_id = db.Column(db.Integer, db.ForeignKey('room.id'), nullable=False)
    joined_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    __table_args__ = (db.UniqueConstraint('user_id', 'room_id'),)

class Message(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    content_encrypted = db.Column(db.Text, nullable=False)  # Encrypted message content
    sender_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    room_id = db.Column(db.Integer, db.ForeignKey('room.id'), nullable=False)
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)
    message_id = db.Column(db.String(36), unique=True, default=lambda: str(uuid.uuid4()))
    
    def __repr__(self):
        return f'<Message {self.id} from {self.sender.username}>'
