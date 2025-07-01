from flask import Blueprint, request, jsonify
from models.order import Order
from models.plans import PricingPlan
from database.db import db
from sqlalchemy.exc import SQLAlchemyError
from middleware.auth_middleware import token_required, admin_required
from models.user import User  # ✅ import đúng model User

order_bp = Blueprint('order', __name__)

# ✅ Lấy tất cả đơn hàng (Admin)
@order_bp.route('/admin', methods=['GET'])
@token_required
@admin_required
def get_all_orders():
    try:
        print("📥 [DEBUG] Gọi API: GET /admin")
        orders = Order.query.all()
        print(f"📦 [DEBUG] Tổng đơn hàng: {len(orders)}")

        if not orders:
            return jsonify({"message": "Hiện chưa có đơn hàng nào!", "orders": []}), 200

        return jsonify({
            "message": "Lấy danh sách đơn hàng thành công!",
            "orders": [order.to_dict() for order in orders]
        }), 200

    except SQLAlchemyError as e:
        print("❌ [ERROR] Lỗi khi lấy tất cả đơn hàng:", str(e))
        return jsonify({"message": "Lỗi khi lấy danh sách đơn hàng!", "error": str(e)}), 500

# ✅ Lấy đơn hàng của người dùng hiện tại
@order_bp.route('/my-orders', methods=['GET'])
@token_required
def get_user_orders():
    try:
        user_id = request.user['user_id']
        print(f"📥 [DEBUG] Gọi API: /my-orders - user_id: {user_id}")

        orders = Order.query.filter_by(user_id=user_id).all()
        print(f"📦 [DEBUG] Đơn hàng của user: {len(orders)}")

        if not orders:
            return jsonify({"message": "Bạn chưa có đơn hàng nào!", "orders": []}), 200

        return jsonify({
            "message": "Lấy đơn hàng thành công!",
            "orders": [order.to_dict() for order in orders]
        }), 200

    except SQLAlchemyError as e:
        print("❌ [ERROR] Lỗi khi lấy đơn hàng người dùng:", str(e))
        return jsonify({"message": "Lỗi khi lấy đơn hàng của bạn!", "error": str(e)}), 500

# ✅ Lấy đơn hàng theo ID
@order_bp.route('/<int:order_id>', methods=['GET'])
@token_required
def get_order(order_id):
    try:
        print(f"📥 [DEBUG] Gọi API: GET /{order_id}")
        order = Order.query.get(order_id)

        if not order:
            print(f"⚠️ [DEBUG] Không tìm thấy đơn hàng ID {order_id}")
            return jsonify({"message": f"Không tìm thấy đơn hàng ID {order_id}!"}), 404

        return jsonify({
            "message": "Lấy đơn hàng thành công!",
            "order": order.to_dict()
        }), 200

    except SQLAlchemyError as e:
        print("❌ [ERROR] Lỗi khi lấy đơn hàng:", str(e))
        return jsonify({"message": "Lỗi khi lấy đơn hàng!", "error": str(e)}), 500

# ✅ Tạo đơn hàng mới
@order_bp.route('/add', methods=['POST'])
@token_required
def create_order():
    try:
        data = request.get_json()
        print("📥 [DEBUG] Dữ liệu nhận từ client:", data)

        user_id = request.user['user_id']
        print("👤 [DEBUG] User ID:", user_id)

        plan_id = data.get('plan_id')
        if not plan_id:
            print("⚠️ [DEBUG] Thiếu plan_id")
            return jsonify({"message": "Thiếu plan_id!"}), 400

        plan = PricingPlan.query.get(plan_id)
        print("🔎 [DEBUG] Gói tìm được:", plan)

        if not plan:
            return jsonify({"message": "Gói không tồn tại!"}), 404

        order = Order(
            user_id=user_id,
            plan_id=plan.id,
            total=float(plan.price_vnd),
            status='pending'
        )
        db.session.add(order)
        db.session.commit()

        print("✅ [DEBUG] Đơn hàng tạo thành công:", order.to_dict())
        return jsonify({
            "message": "Tạo đơn hàng thành công!",
            "order": order.to_dict()
        }), 201

    except SQLAlchemyError as e:
        db.session.rollback()
        print("❌ [ERROR] Lỗi khi tạo đơn hàng:", str(e))
        return jsonify({"message": "Lỗi khi tạo đơn hàng!", "error": str(e)}), 500

# ✅ Cập nhật trạng thái đơn hàng (Admin)
@order_bp.route('/<int:order_id>/status', methods=['PUT'])
@token_required
@admin_required
def update_order_status(order_id):
    try:
        data = request.get_json()
        new_status = data.get('status')
        print(f"📥 [DEBUG] Cập nhật trạng thái đơn hàng ID {order_id} => '{new_status}'")

        valid_statuses = ['pending', 'paid', 'cancelled', 'completed']
        if new_status not in valid_statuses:
            print("⚠️ [DEBUG] Trạng thái không hợp lệ")
            return jsonify({
                "message": f"Trạng thái không hợp lệ! Chỉ chấp nhận: {valid_statuses}"
            }), 400

        order = Order.query.get(order_id)
        if not order:
            return jsonify({"message": f"Không tìm thấy đơn hàng ID {order_id}!"}), 404

        order.status = new_status
        db.session.commit()

        print("✅ [DEBUG] Trạng thái cập nhật thành công:", order.to_dict())
        return jsonify({
            "message": "Cập nhật trạng thái thành công!",
            "order": order.to_dict()
        }), 200

    except SQLAlchemyError as e:
        db.session.rollback()
        print("❌ [ERROR] Lỗi khi cập nhật trạng thái đơn hàng:", str(e))
        return jsonify({"message": "Lỗi khi cập nhật trạng thái đơn hàng!", "error": str(e)}), 500


@order_bp.route('/confirm-payment/<int:order_id>', methods=['POST'])
@token_required
def confirm_payment(order_id):
    try:
        print(f"[DEBUG] Xác nhận thanh toán cho order_id: {order_id}")
        order = Order.query.get(order_id)

        if not order:
            return jsonify({"message": f"Không tìm thấy đơn hàng với ID {order_id}"}), 404

        if order.status == "paid":
            return jsonify({"message": "Đơn hàng đã được thanh toán"}), 200

        # ✅ Lấy thông tin plan và user
        plan = PricingPlan.query.get(order.plan_id)
        user = User.query.get(order.user_id)

        if not plan or not user:
            return jsonify({"message": "Không thể xác định gói hoặc người dùng!"}), 400

        # ✅ Xử lý cộng credits
        try:
            plan_credits = int(plan.credits.replace(",", "").strip())
        except Exception as e:
            print(f"[WARNING] Không thể phân tích credits: {plan.credits}, lỗi: {str(e)}")
            plan_credits = 0

        user.credits += plan_credits
        order.status = "paid"

        db.session.commit()

        return jsonify({
            "message": f"Xác nhận thanh toán thành công. +{plan_credits} credits!",
            "user_id": user.id,
            "user_credits": user.credits,
            "order_id": order.id,
            "status": order.status
        }), 200

    except Exception as e:
        db.session.rollback()
        return jsonify({"message": "Lỗi xác nhận thanh toán", "error": str(e)}), 500
@order_bp.route('/confirm-payment-request/<int:order_id>', methods=['POST'])
@token_required
def request_confirm_payment(order_id):
    try:
        print(f"[DEBUG] Người dùng xác nhận đã thanh toán - order_id: {order_id}")
        order = Order.query.get(order_id)

        if not order:
            return jsonify({"message": "Không tìm thấy đơn hàng!"}), 404

        if order.status != "pending":
            return jsonify({"message": f"Đơn hàng hiện tại không thể xác nhận, trạng thái: {order.status}"}), 400

        order.status = "pending"
        db.session.commit()

        return jsonify({
            "message": "Đã gửi yêu cầu xác nhận thanh toán. Vui lòng chờ admin duyệt!",
            "order_id": order.id,
            "status": order.status
        }), 200

    except Exception as e:
        db.session.rollback()
        return jsonify({"message": "Lỗi gửi yêu cầu xác nhận thanh toán", "error": str(e)}), 500
@order_bp.route('/admin-confirm-payment/<int:order_id>', methods=['POST'])
@token_required
@admin_required
def admin_confirm_payment(order_id):
    try:
        print(f"[DEBUG] Admin duyệt đơn hàng - order_id: {order_id}")
        order = Order.query.get(order_id)

        if not order:
            return jsonify({"message": "Không tìm thấy đơn hàng!"}), 404

        if order.status != "pending":
            return jsonify({"message": "Đơn hàng chưa được xác nhận từ phía người dùng!"}), 400

        plan = PricingPlan.query.get(order.plan_id)
        user = User.query.get(order.user_id)

        if not plan or not user:
            return jsonify({"message": "Không thể xác định gói hoặc người dùng!"}), 400

        try:
            credits_to_add = int(plan.credits.replace(",", "").strip())
        except Exception as e:
            print(f"[WARNING] Lỗi phân tích credits: {e}")
            credits_to_add = 0

        user.credits += credits_to_add
        order.status = "paid"

        db.session.commit()

        return jsonify({
            "message": "Admin đã duyệt thanh toán thành công!",
            "user_id": user.id,
            "credits_đã_cộng": credits_to_add,
            "tổng_credits": user.credits,
            "order_id": order.id
        }), 200

    except Exception as e:
        db.session.rollback()
        return jsonify({"message": "Lỗi admin duyệt thanh toán", "error": str(e)}), 500
@order_bp.route('/stats', methods=['GET'])
@token_required
@admin_required
def order_stats():
    try:
        total_orders = Order.query.count()
        total_revenue = db.session.query(db.func.sum(Order.total)).scalar() or 0
        pending_orders = Order.query.filter_by(status='pending').count()
        paid_orders = Order.query.filter_by(status='paid').count()

        return jsonify({
            "total_orders": total_orders,
            "total_revenue": total_revenue,
            "pending_orders": pending_orders,
            "paid_orders": paid_orders
        }), 200
    except Exception as e:
        print("❌ [ERROR] Lỗi khi lấy thống kê đơn hàng:", str(e))
        return jsonify({"message": "Lỗi khi lấy thống kê đơn hàng!", "error": str(e)}), 500

