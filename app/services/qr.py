"""
Генерация QR-кодов.
"""

import io
import qrcode
from app.config import settings

def generate_qr_code(building_id: int) -> io.BytesIO:
    url = f"{settings.MINI_APP_URL}/?building_id={building_id}"
    qr = qrcode.QRCode(
        version=1,
        error_correction=qrcode.constants.ERROR_CORRECT_M,
        box_size=10,
        border=4,
    )
    qr.add_data(url)
    qr.make(fit=True)
    img = qr.make_image(fill_color="black", back_color="white")
    buffer = io.BytesIO()
    img.save(buffer, format="PNG")
    buffer.seek(0)
    return buffer
