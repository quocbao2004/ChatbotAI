from flask import Blueprint, request, jsonify
import pickle
import random
from flask_cors import CORS
from datetime import datetime
from app.extensions import db
from flask_jwt_extended import jwt_required, get_jwt_identity
from sqlalchemy import text

chat_bp = Blueprint('chat', __name__)
CORS(chat_bp, supports_credentials=True)

@chat_bp.route('/chat', methods=['POST'])
@jwt_required()
def chat():
    data = request.get_json()
    message = data.get('message')
    if not message:
        return jsonify({'error': 'Missing message'}), 400

    user_id = get_jwt_identity()

    # 🔍 Kiểm tra xem user đã có session chưa
    session = db.session.execute(text("""
        SELECT session_id FROM chat_sessions
        WHERE user_id = :uid
        LIMIT 1
    """), {'uid': user_id}).fetchone()

    # ➕ Nếu chưa có, tạo mới
    if not session:
        db.session.execute(text("""
            INSERT INTO chat_sessions (user_id, start_time)
            VALUES (:uid, :start_time)
        """), {'uid': user_id, 'start_time': datetime.utcnow()})
        db.session.commit()

        session = db.session.execute(text("""
            SELECT session_id FROM chat_sessions
            WHERE user_id = :uid
            LIMIT 1
        """), {'uid': user_id}).fetchone()

    session_id = session.session_id
    response = "Xin lỗi, tôi không hiểu bạn nói gì 😅"

    # 🤖 Xử lý chatbot
    try:
        with open('chatbot_model.pkl', 'rb') as f:
            model, vectorizer, intents_data = pickle.load(f)

        X = vectorizer.transform([message])
        predicted_tag = model.predict(X)[0]

        for intent in intents_data['intents']:
            if intent['tag'] == predicted_tag:
                response = random.choice(intent['responses'])
                break
    except Exception as e:
        print("❌ Lỗi xử lý chatbot:", str(e))

    # 💬 Lưu tin nhắn user
    db.session.execute(text("""
        INSERT INTO chat_messages (session_id, sender, message_text, created_at)
        VALUES (:sid, 'user', :msg, :created)
    """), {
        'sid': session_id,
        'msg': message,
        'created': datetime.utcnow()
    })

    # 💬 Lưu tin nhắn bot
    db.session.execute(text("""
        INSERT INTO chat_messages (session_id, sender, message_text, created_at)
        VALUES (:sid, 'bot', :msg, :created)
    """), {
        'sid': session_id,
        'msg': response,
        'created': datetime.utcnow()
    })

    db.session.commit()

    # 📜 Lấy lịch sử chat
    messages = db.session.execute(text("""
        SELECT sender, message_text, created_at FROM chat_messages
        WHERE session_id = :sid
        ORDER BY created_at
    """), {'sid': session_id}).fetchall()

    history = [
        {
            'text': msg.message_text,
            'sender': msg.sender,
            'created_at': msg.created_at.isoformat()
        } for msg in messages
    ]

    return jsonify({
        'response': response,
        'history': history,
        'session_id': session_id
    })

@chat_bp.route('/chat/history', methods=['GET'])
@jwt_required()
def chat_history():
    session_id = 1
    if not session_id:
        return jsonify({'error': 'Missing session_id'}), 400

    messages = db.session.execute(text("""
        SELECT sender, message_text, created_at FROM chat_messages
        WHERE session_id = :sid
        ORDER BY created_at
    """), {'sid': session_id}).fetchall()

    return jsonify([
        {
            'text': msg.message_text,
            'sender': msg.sender,
            'created_at': msg.created_at.isoformat()
        } for msg in messages
    ])

@chat_bp.route('/chat/delete', methods=['DELETE'])
@jwt_required()
def delete_chat_session():
    session_id = 1
    if not session_id:
        return jsonify({'error': 'Missing session_id'}), 400

    try:
        # Xóa tất cả tin nhắn thuộc session
        db.session.execute(text("""
            DELETE FROM chat_messages WHERE session_id = 1
        """))


        db.session.commit()
        return jsonify({'message': 'Đã xóa toàn bộ đoạn chat và session'}), 200

    except Exception as e:
        db.session.rollback()
        return jsonify({'error': f'Không thể xóa đoạn chat: {str(e)}'}), 500