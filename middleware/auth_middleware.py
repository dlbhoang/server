from functools import wraps
from flask import request, jsonify
from utils.jwt_utils import decode_token

def token_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        token = None
        if 'Authorization' in request.headers:
            token = request.headers['Authorization'].split(" ")[1]
        if not token:
            return jsonify({'message': 'Thiếu token!'}), 401

        data = decode_token(token)
        if not data:
            return jsonify({'message': 'Token không hợp lệ hoặc hết hạn!'}), 403

        request.user = data
        return f(*args, **kwargs)
    return decorated

def admin_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        if not hasattr(request, 'user'):
            return jsonify({'message': 'Chưa xác thực!'}), 401
        if request.user.get('role') != 'admin':
            return jsonify({'message': 'Chỉ quản trị viên mới có quyền thực hiện thao tác này!'}), 403
        return f(*args, **kwargs)
    return decorated