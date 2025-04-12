from qrcode.main import QRCode


def display_url_as_qr(url):
    print(url)
    qr = QRCode()
    qr.add_data(url)
    qr.make(fit=True)
    img = qr.make_image()
    img.show()
