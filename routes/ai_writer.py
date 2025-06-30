from flask import Blueprint, request, jsonify
from models.user import User
from models.ai_article import AIArticleHistory
from utils.ai_writer_helper import generate_article
from middleware.auth_middleware import token_required
from database.db import db

ai_writer_bp = Blueprint('ai_writer', __name__)

@ai_writer_bp.route('/generate', methods=['POST'])
@token_required
def generate_ai_article():
    try:
        data = request.get_json()
        user_id = request.user['user_id']
        user = User.query.get(user_id)

        if not user:
            return jsonify({"message": "Không tìm thấy người dùng!"}), 404

        # Gọi hàm sinh bài viết
        article = generate_article(data, user)

        # Lưu lịch sử bài viết
        history = AIArticleHistory(
            user_id=user.id,
            title=article['title'],
            outline=article['outline'],
            content=article['content'],
            model_used=article['model_used'],
            website=article['website']
        )
        db.session.add(history)

        # Commit để lưu credits và lịch sử
        db.session.commit()

        return jsonify({
            "message": "Viết bài thành công!",
            "credits_remaining": user.credits,
            "article": article
        }), 200

    except Exception as e:
        db.session.rollback()
        return jsonify({"message": "Lỗi khi viết bài", "error": str(e)}), 500

@ai_writer_bp.route('/history', methods=['GET'])
@token_required
def get_ai_article_history():
    try:
        user_id = request.user['user_id']
        articles = AIArticleHistory.query.filter_by(user_id=user_id).order_by(AIArticleHistory.created_at.desc()).all()

        result = []
        for article in articles:
            result.append({
                "id": article.id,
                "title": article.title,
                "outline": article.outline,
                "content": article.content,
                "model_used": article.model_used,
                "website": article.website,
                "created_at": article.created_at.strftime('%Y-%m-%d %H:%M:%S')
            })

        return jsonify({
            "message": "Lấy lịch sử thành công!",
            "history": result
        }), 200

    except Exception as e:
        return jsonify({"message": "Lỗi khi lấy lịch sử", "error": str(e)}), 500
