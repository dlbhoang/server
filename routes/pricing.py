from flask import Blueprint, request, jsonify
from models.plans import PricingPlan
from database.db import db
from sqlalchemy.exc import SQLAlchemyError
from middleware.auth_middleware import token_required, admin_required

pricing_bp = Blueprint('pricing', __name__)

# GET all pricing plans
@pricing_bp.route('/plans', methods=['GET'])
def get_plans():
    try:
        plans = PricingPlan.query.all()
        if not plans:
            return jsonify({"message": "Hiện tại chưa có gói nào được tạo!"}), 200
        return jsonify([plan.to_dict() for plan in plans]), 200
    except SQLAlchemyError as e:
        return jsonify({"message": "Lỗi khi lấy danh sách gói!", "error": str(e)}), 500

# GET single plan
@pricing_bp.route('/plans/<int:plan_id>', methods=['GET'])
def get_plan(plan_id):
    try:
        plan = PricingPlan.query.get(plan_id)
        if not plan:
            return jsonify({
                "message": f"Gói với ID {plan_id} không tồn tại!",
                "status": 404
            }), 404
        return jsonify({
            "message": "Lấy thông tin gói thành công!",
            "plan": plan.to_dict()
        }), 200
    except SQLAlchemyError as e:
        return jsonify({
            "message": "Đã xảy ra lỗi khi truy xuất gói!",
            "error": str(e)
        }), 500

# CREATE a plan
@pricing_bp.route('/plans', methods=['POST'])
@token_required
@admin_required
def create_plan():
    try:
        data = request.get_json()

        required_fields = ['name', 'price', 'vnd', 'credits', 'posts', 'keywordTools', 'seoTools', 'payUrl']
        for field in required_fields:
            if field not in data:
                return jsonify({"message": f"Thiếu trường bắt buộc: {field}"}), 400

        plan = PricingPlan(
            name=data['name'],
            price_usd=data['price'],
            price_vnd=data['vnd'],
            credits=data['credits'],
            posts=data['posts'],
            keyword_tools=data['keywordTools'],
            seo_tools=data['seoTools'],
            pay_url=data['payUrl']
        )
        db.session.add(plan)
        db.session.commit()
        return jsonify({"message": "Tạo gói thành công!", "plan": plan.to_dict()}), 201
    except SQLAlchemyError as e:
        db.session.rollback()
        return jsonify({"message": "Lỗi khi tạo gói!", "error": str(e)}), 500

# UPDATE a plan
@pricing_bp.route('/plans/<int:plan_id>', methods=['PUT'])
@token_required
@admin_required
def update_plan(plan_id):
    try:
        plan = PricingPlan.query.get(plan_id)
        if not plan:
            return jsonify({
                "message": f"Gói với ID {plan_id} không tồn tại!",
                "status": 404
            }), 404

        data = request.get_json()
        plan.name = data.get('name', plan.name)
        plan.price_usd = data.get('price', plan.price_usd)
        plan.price_vnd = data.get('vnd', plan.price_vnd)
        plan.credits = data.get('credits', plan.credits)
        plan.posts = data.get('posts', plan.posts)
        plan.keyword_tools = data.get('keywordTools', plan.keyword_tools)
        plan.seo_tools = data.get('seoTools', plan.seo_tools)
        plan.pay_url = data.get('payUrl', plan.pay_url)

        db.session.commit()
        return jsonify({"message": "Cập nhật gói thành công!", "plan": plan.to_dict()}), 200
    except SQLAlchemyError as e:
        db.session.rollback()
        return jsonify({"message": "Lỗi khi cập nhật gói!", "error": str(e)}), 500

# DELETE a plan
@pricing_bp.route('/plans/<int:plan_id>', methods=['DELETE'])
@token_required
@admin_required
def delete_plan(plan_id):
    try:
        plan = PricingPlan.query.get(plan_id)
        if not plan:
            return jsonify({
                "message": f"Gói với ID {plan_id} không tồn tại!",
                "status": 404
            }), 404

        db.session.delete(plan)
        db.session.commit()
        return jsonify({
            "message": f"Đã xoá gói có ID {plan_id} thành công.",
            "status": 200
        }), 200
    except SQLAlchemyError as e:
        db.session.rollback()
        return jsonify({
            "message": "Đã xảy ra lỗi khi xoá gói.",
            "error": str(e),
            "status": 500
        }), 500
