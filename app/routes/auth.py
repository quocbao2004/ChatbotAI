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
