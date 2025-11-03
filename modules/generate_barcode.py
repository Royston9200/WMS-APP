from barcode import get_barcode_class
from barcode.writer import ImageWriter
from datetime import datetime


def generate_ean13(data: str, filename: str, username: str):
    EAN13 = get_barcode_class("ean13")
    code = EAN13(data, writer=ImageWriter())
    
    with open("logs.txt", "a") as log:
        log.write(f"{username} genereerde een barcode op {datetime.now()}\n")
    
    return code.save(f"static/{filename}")

