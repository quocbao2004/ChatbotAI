from flask import Flask
from app.extensions import db, jwt, mail
from app.routes.auth import auth_bp
from app.config import Config
from app.routes.quiz import quiz_bp
from app.routes.chat import chat_bp
from app.models.user import User
from flask_cors import CORS
from flask_jwt_extended import jwt_required, get_jwt_identity 
from flask_jwt_extended import JWTManager

jwt = JWTManager()
def load_user(user_id):
    return User.query.get(int(user_id))

def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)
    print("🔑 JWT_SECRET_KEY đang dùng:", app.config["JWT_SECRET_KEY"])

    db.init_app(app)
    jwt.init_app(app)
    mail.init_app(app)
    app.register_blueprint(quiz_bp)
    app.register_blueprint(auth_bp)
    app.register_blueprint(chat_bp)
    CORS(app, resources={
    r"/auth/*": {
        "origins": "http://localhost:3000",
        "allow_headers": ["Content-Type", "Authorization"],
        "expose_headers": ["Authorization"]
    }
    }, supports_credentials=True)

    with app.app_context():
        db.create_all()

    return app
