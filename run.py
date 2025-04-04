from app import create_app
from app.extensions import db
from dotenv import load_dotenv
from flask_cors import CORS

load_dotenv()  # Tải biến môi trường từ .env

app = create_app()
CORS(app, supports_credentials=True, origins="http://localhost:3000")
if __name__ == "__main__":
    with app.app_context():
        db.create_all()
    app.run(debug=True)
