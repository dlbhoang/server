from database.db import db
from utils.seapay import generate_vietqr_url  # Hàm tạo QR động dạng URL ảnh

class PricingPlan(db.Model):
    __tablename__ = 'plans'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    price_usd = db.Column(db.String(20), nullable=False)
    price_vnd = db.Column(db.String(50), nullable=False)
    credits = db.Column(db.String(20))
    posts = db.Column(db.String(20))
    keyword_tools = db.Column(db.String(100))
    seo_tools = db.Column(db.String(100))
    pay_url = db.Column(db.String(300))  # Optional: có thể bỏ vì ta tự generate

    def to_dict(self):
        qr_url = generate_vietqr_url(self)  # → QR SePay động

        return {
            "id": self.id,
            "name": self.name,
            "price": self.price_usd,
            "vnd": self.price_vnd,
            "credits": self.credits,
            "posts": self.posts,
            "keywordTools": self.keyword_tools,
            "seoTools": self.seo_tools,
            "payUrl": qr_url  # Gán trực tiếp vào payUrl
        }
