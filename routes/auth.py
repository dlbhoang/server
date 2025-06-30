import re
import jwt
import datetime
from flask import Blueprint, request, jsonify
from models.user import User
from database.db import db
from extensions.security import hash_password, verify_password
from utils.jwt_utils import generate_token, decode_token
from middleware.auth_middleware import token_required

auth_bp = Blueprint('auth', __name__)

# Regex validation

def is_valid_email(email):
    return re.match(r"^[\w\.-]+@[\w\.-]+\.\w+$", email)

def is_valid_phone(phone):
    return re.match(r"^0\d{9}$", phone)

# Register
@auth_bp.route('/register', methods=['POST'])
def register():
    data = request.get_json()

    email = data.get('email')
    password = data.get('password')
    name = data.get('name')
    phone = data.get('phone')
    role = data.get('role', 'user')

    if not all([email, password, name]):
        return jsonify({'message': 'Thiếu thông tin bắt buộc!'}), 400

    if not is_valid_email(email):
        return jsonify({'message': 'Email không hợp lệ!'}), 400

    if phone and not is_valid_phone(phone):
        return jsonify({'message': 'Số điện thoại không hợp lệ!'}), 400

    if User.query.filter_by(email=email).first():
        return jsonify({'message': 'Email đã tồn tại!'}), 400

    user = User(
        email=email,
        password=hash_password(password),
        name=name,
        phone=phone,
        role=role
    )

    db.session.add(user)
    db.session.commit()

    return jsonify({'message': 'Đăng ký thành công', 'user': user.to_dict()}), 201

# Login
@auth_bp.route('/login', methods=['POST'])
def login():
    data = request.get_json()

    email = data.get('email')
    password = data.get('password')

    if not all([email, password]):
        return jsonify({'message': 'Thiếu email hoặc mật khẩu!'}), 400

    user = User.query.filter_by(email=email).first()
    if not user or not verify_password(password, user.password):
        return jsonify({'message': 'Email hoặc mật khẩu không đúng!'}), 401

    token = generate_token(user.id, user.role)

    return jsonify({
        'message': 'Đăng nhập thành công',
        'token': token,
        'user': user.to_dict()
    }), 200

# Update profile
@auth_bp.route('/update-profile', methods=['PUT'])
@token_required
def update_profile():
    user_id = request.user['user_id']
    user = User.query.get(user_id)
    if not user:
        return jsonify({'message': 'Không tìm thấy người dùng!'}), 404

    data = request.get_json()
    user.name = data.get('name', user.name)
    user.phone = data.get('phone', user.phone)

    db.session.commit()
    return jsonify({'message': 'Cập nhật hồ sơ thành công!', 'user': user.to_dict()}), 200

# Change password
@auth_bp.route('/change-password', methods=['PUT'])
@token_required
def change_password():
    user_id = request.user['user_id']
    user = User.query.get(user_id)
    data = request.get_json()

    old_pass = data.get('old_password')
    new_pass = data.get('new_password')

    if not verify_password(old_pass, user.password):
        return jsonify({'message': 'Mật khẩu cũ không đúng!'}), 400

    user.password = hash_password(new_pass)
    db.session.commit()
    return jsonify({'message': 'Đổi mật khẩu thành công!'}), 200
