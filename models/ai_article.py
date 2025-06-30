
from database.db import db
from datetime import datetime

class AIArticleHistory(db.Model):
    __tablename__ = 'ai_article_history'

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, nullable=False)
    title = db.Column(db.String(255), nullable=False)
    outline = db.Column(db.Text)
    content = db.Column(db.Text, nullable=False)
    model_used = db.Column(db.String(100))
    website = db.Column(db.String(255))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
