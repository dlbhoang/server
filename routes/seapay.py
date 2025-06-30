from flask import Blueprint, jsonify
from models.plans import PricingPlan
from utils.seapay import generate_vietqr_url

seapay_bp = Blueprint("seapay", __name__)

@seapay_bp.route("/generate-qr/<int:plan_id>", methods=["GET"])
def generate_qr(plan_id):
    plan = PricingPlan.query.get(plan_id)
    if not plan:
        return jsonify({"error": "Gói không tồn tại"}), 404

    qr_url = generate_vietqr_url(plan)
    if qr_url:
        return jsonify({
            "plan_id": plan.id,
            "name": plan.name,
            "amount_vnd": plan.price_vnd,
            "qr_code_url": qr_url
        })
    else:
        return jsonify({"error": "Không tạo được QR code"}), 500
