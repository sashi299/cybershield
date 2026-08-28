import io
import cv2
import numpy as np
from PIL import Image

def decode_qr(image_bytes: bytes) -> str:
    # 1. Try pyzbar if available
    try:
        from pyzbar.pyzbar import decode
        image = Image.open(io.BytesIO(image_bytes))
        decoded_objects = decode(image)
        if decoded_objects and decoded_objects[0].data:
            return decoded_objects[0].data.decode('utf-8')
    except Exception:
        pass

    # 2. Try OpenCV QRCodeDetector (100% native Python/C++, zero OS dependencies)
    try:
        np_arr = np.frombuffer(image_bytes, np.uint8)
        img_cv = cv2.imdecode(np_arr, cv2.IMREAD_COLOR)
        if img_cv is not None:
            detector = cv2.QRCodeDetector()
            data, bbox, _ = detector.detectAndDecode(img_cv)
            if data and data.strip():
                return data.strip()

            # Try grayscale + thresholding if initial detection missed
            gray = cv2.cvtColor(img_cv, cv2.COLOR_BGR2GRAY)
            data, bbox, _ = detector.detectAndDecode(gray)
            if data and data.strip():
                return data.strip()

            _, thresh = cv2.threshold(gray, 128, 255, cv2.THRESH_BINARY | cv2.THRESH_OTSU)
            data, bbox, _ = detector.detectAndDecode(thresh)
            if data and data.strip():
                return data.strip()
    except Exception:
        pass

    raise ValueError("No valid QR code could be detected in the provided image.")
