from PIL import Image
from qrcode.main import QRCode


def display_url_as_qr(url: str) -> Image:
    qr = QRCode()
    qr.add_data(url)
    qr.make()

    img = qr.make_image()

    return img
