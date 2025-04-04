from app.extensions import db

class ChatSession(db.Model):
    __tablename__ = 'chat_sessions'
    __table_args__ = {'extend_existing': True}

    id = db.Column(db.Integer, primary_key=True)
    current_user_id = db.Column(db.Integer, db.ForeignKey('users.user_id'))  # OK
    started_at = db.Column(db.DateTime, nullable=False)

    user = db.relationship('User', backref='chat_sessions')  # Tên chuẩn hơn là 'user'
