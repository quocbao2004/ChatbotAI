from app.extensions import db
from datetime import datetime
from app.models.chat_session import ChatSession

# chat_message.py

class ChatMessage(db.Model):
    __tablename__ = 'chat_messages'

    message_id = db.Column(db.Integer, primary_key=True)
    session_id = db.Column(db.Integer, db.ForeignKey('chat_sessions.session_id'), nullable=False)
    sender = db.Column(db.String(50), nullable=False)
    message_text = db.Column(db.Text, nullable=False)
    created_at = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)

# Sau cùng trong file (hoặc tại __init__.py của models)
# Import ChatSession trước
from app.models.chat_session import ChatSession

ChatMessage.session = db.relationship('ChatSession', backref=db.backref('messages', lazy=True))
