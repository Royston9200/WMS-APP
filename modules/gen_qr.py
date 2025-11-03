import qrcode


data = "1A/0/1/1"


qr = qrcode.QRCode(
    version=1,
    error_correction=qrcode.constants.ERROR_CORRECT_L,
    box_size=10,
    border=4,
)

qr.add_data(data)
qr.make(fit=True)


img = qr.make_image(fill_color="black", back_color="white")


img.save("qr_1A_0_1_1.png")
