import urllib.parse

SEAPAY_ACCOUNT = "88865298888"     # Số tài khoản nhận tiền
SEAPAY_BANK_CODE = "tp"         # Mã ngân hàng

def generate_vietqr_url(plan):
    try:
        amount_str = plan.price_vnd.replace(",", "").replace("₫", "").replace(".", "").strip()
        amount = int(amount_str)
        description = f"Mua gói {plan.name}"
        encoded_des = urllib.parse.quote(description)

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
