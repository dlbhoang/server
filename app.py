from flask import Flask
from flask_cors import CORS
from database.db import db
from routes.auth import auth_bp
from routes.pricing import pricing_bp
from routes.order import order_bp
from routes.seapay import seapay_bp
from routes.ai_writer import ai_writer_bp
import os
from dotenv import load_dotenv

# Load biến môi trường
load_dotenv()

app = Flask(__name__)
CORS(app)

# 🔧 Cấu hình cơ sở dữ liệu
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///users.db'  # Bạn có thể đổi sang PostgreSQL/MySQL khi cần
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SECRET_KEY'] = os.getenv("SECRET_KEY", "your_secret_key")  # JWT secret

# 🔧 Khởi tạo DB
db.init_app(app)

# ✅ Đăng ký các blueprint (routes)
app.register_blueprint(auth_bp, url_prefix='/api/auth')
app.register_blueprint(pricing_bp, url_prefix='/api')
app.register_blueprint(order_bp, url_prefix='/api/orders')
app.register_blueprint(seapay_bp, url_prefix='/api/seapay')
app.register_blueprint(ai_writer_bp, url_prefix='/api/ai-writer')

# ✅ Tạo bảng DB nếu chưa tồn tại
with app.app_context():
    db.create_all()

# ✅ Chạy app
if __name__ == '__main__':
    app.run(debug=True)
