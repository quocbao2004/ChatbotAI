from flask import Blueprint, request, jsonify
from app.extensions import db, mail
from flask_mail import Message
from app.models.user import User
from flask_jwt_extended import create_access_token
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime, timedelta
import random
from flask_cors import CORS
from flask_jwt_extended import jwt_required, get_jwt_identity

from flask import request, jsonify, current_app
from flask_jwt_extended import create_access_token

auth_bp = Blueprint('auth', __name__)
CORS(auth_bp)
# In-memory OTP store
otp_store = {}

@auth_bp.route('/auth/register', methods=['POST'])
def send_otp():
    data = request.get_json()
    email = data.get('email')

    if User.query.filter_by(email=email).first():
        return jsonify({'message': 'Email already registered'}), 400

    otp = str(random.randint(100000, 999999))
    otp_store[email] = {
        'otp': otp,
        'expires_at': datetime.utcnow() + timedelta(minutes=1)
    }

    msg = Message(subject='Your OTP Code',
                  recipients=[email],
                  body=f'Your OTP is: {otp}')
    mail.send(msg)

    return jsonify({'message': 'OTP sent to your email'}), 200


@auth_bp.route('/auth/verify-otp', methods=['POST'])
def verify_otp():
    data = request.get_json()
    email = data.get('email')
    otp = data.get('otp')
    username = data.get('username')
    password = data.get('password')

    otp_data = otp_store.get(email)
    if not otp_data:
        return jsonify({'message': 'No OTP found'}), 400

    if datetime.utcnow() > otp_data['expires_at']:
        del otp_store[email]
        return jsonify({'message': 'OTP expired'}), 400

    if otp_data['otp'] != otp:
        return jsonify({'message': 'Invalid OTP'}), 400

    hashed_pw = generate_password_hash(password)
    user = User(username=username, email=email, password=hashed_pw, role="student")
    db.session.add(user)
    db.session.commit()

    del otp_store[email]  # Clean up
    return jsonify({'message': 'User registered successfully'}), 201


@auth_bp.route('/auth/login', methods=['POST'])
def login():
    data = request.get_json()
    email = data.get('email')
    password = data.get('password')

    user = User.query.filter_by(email=email).first()

    if not user or not check_password_hash(user.password, password):
        return jsonify({'message': 'Invalid credentials'}), 401
    access_token = create_access_token(identity=str(user.user_id))
    return jsonify({'access_token': access_token}), 200

@auth_bp.route('/auth/profile', methods=['GET'])
@jwt_required()
def get_user_profile():
    print("✅ /auth/profile accessed")
    user_id = get_jwt_identity()
    print("🔐 Token contains user_id:", user_id)

    user = User.query.get(user_id)
    if not user:
        return jsonify({'message': 'User not found'}), 404

    return jsonify({
        'username': user.username,
        'email': user.email,
        'role': user.role
    }), 200



#DOI MK SU DUNG MK HIEN TAI
@auth_bp.route('/auth/change-password', methods=['POST'])
def change_password():
    data = request.get_json()
    email = data.get('email')
    current_password = data.get('current_password')
    new_password = data.get('new_password')

    
    user = User.query.filter_by(email=email).first()
    if not user:
        return jsonify({'message': 'User not found'}), 404

    
    if not check_password_hash(user.password, current_password):
        return jsonify({'message': 'Current password is incorrect'}), 401

    
    hashed_new_password = generate_password_hash(new_password)
    user.password = hashed_new_password
    db.session.commit()

    return jsonify({'message': 'Password changed successfully'}), 200

reset_otp_store = {}

#DOI MK SU DUNG OTP TU EMAIL
@auth_bp.route('/auth/forgot-password', methods=['POST'])
def forgot_password():
    data = request.get_json()
    email = data.get('email')

    user = User.query.filter_by(email=email).first()
    if not user:
        return jsonify({'message': 'Email not registered'}), 404

    otp = str(random.randint(100000, 999999))
    reset_otp_store[email] = {
        'otp': otp,
        'expires_at': datetime.utcnow() + timedelta(minutes=50000)
    }

    msg = Message(subject='Password Reset OTP',
                  recipients=[email],
                  body=f'Your OTP for resetting your password is: {otp}')
    mail.send(msg)

    return jsonify({'message': 'OTP sent to your email'}), 200

@auth_bp.route('/auth/reset-password', methods=['POST'])
def reset_password():
    data = request.get_json()
    email = data.get('email')
    otp = data.get('otp')
    new_password = data.get('new_password')

    otp_data = reset_otp_store.get(email)
    if not otp_data:
        return jsonify({'message': 'No OTP found'}), 400

    if datetime.utcnow() > otp_data['expires_at']:
        del reset_otp_store[email]
        return jsonify({'message': 'OTP expired'}), 400

    if otp_data['otp'] != otp:
        return jsonify({'message': 'Invalid OTP'}), 400

    hashed_pw = generate_password_hash(new_password)
    user = User.query.filter_by(email=email).first()
    user.password = hashed_pw
    db.session.commit()

    del reset_otp_store[email]  
    return jsonify({'message': 'Password reset successfully'}), 200