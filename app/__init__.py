from flask import Flask
from app.extensions import db, jwt, mail
from app.routes.auth import auth_bp
from app.config import Config
from app.routes.quiz import quiz_bp
def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)

    db.init_app(app)
    jwt.init_app(app)
    mail.init_app(app)

    app.register_blueprint(quiz_bp)
    app.register_blueprint(auth_bp)

    with app.app_context():
        db.create_all()

    return app
