from flask import Blueprint, request, jsonify
from app.extensions import db, mail
from flask_mail import Message
from app.models.user import User
from flask_jwt_extended import create_access_token
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime, timedelta
import random

auth_bp = Blueprint('auth', __name__)

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

    access_token = create_access_token(identity=user.user_id)
    return jsonify({'access_token': access_token}), 200


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
        'expires_at': datetime.utcnow() + timedelta(minutes=5)
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

#DOI THONG TIN CA NHAN CUA USER
@auth_bp.route('/auth/update-info', methods=['PUT'])
def update_user_info():
    data = request.get_json()
    user_id = data.get('user_id')  
    new_username = data.get('username')
    new_email = data.get('email')
    new_role = data.get('role')

    
    user = User.query.filter_by(user_id=user_id).first()
    if not user:
        return jsonify({'message': 'User not found'}), 404

    
    if new_username:
        user.username = new_username
    if new_email:
        if User.query.filter_by(email=new_email).first():
            return jsonify({'message': 'Email already in use'}), 400
        user.email = new_email
    if new_role:
        user.role = new_role

    
    db.session.commit()

    return jsonify({'message': 'User information updated successfully'}), 200
