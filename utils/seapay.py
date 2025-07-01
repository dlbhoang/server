import urllib.parse

SEAPAY_ACCOUNT = "88865298888"     # Số tài khoản nhận tiền
SEAPAY_BANK_CODE = "TPBank"        # Mã ngân hàng đúng theo URL sepay

def generate_vietqr_url(plan):
    try:
        # Loại bỏ các ký tự không phải số để chuyển sang int
        amount_str = plan.price_vnd.replace(",", "").replace("₫", "").replace(".", "").strip()
        amount = int(amount_str)

        # Mô tả giao dịch
        description = f"Mua gói {plan.name}"
        encoded_des = urllib.parse.quote(description)

        # Tạo URL QR
        return (
            f"https://qr.sepay.vn/img?"
            f"acc={SEAPAY_ACCOUNT}&"
            f"bank={SEAPAY_BANK_CODE}&"
            f"amount={amount}&"
            f"des={encoded_des}"
        )
    except Exception as e:
        print("Lỗi tạo QR:", str(e))
        return None
