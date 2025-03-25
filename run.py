# run.py

from app import create_app
from app.extensions import db
from dotenv import load_dotenv

load_dotenv()  # Tải biến môi trường từ .env

app = create_app()

if __name__ == "__main__":
    with app.app_context():
        db.create_all()
    app.run(debug=True)
