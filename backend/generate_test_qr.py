import qrcode
import os
from PIL import Image

def generate_test_qr_images():
    output_dir = os.path.join(os.path.dirname(__file__), 'test_qr_images')
    os.makedirs(output_dir, exist_ok=True)
    
    # 1. Standard URL QR
    qr = qrcode.make('https://www.google.com')
    qr.save(os.path.join(output_dir, 'standard_url.png'))
    
    # 2. Phishing URL QR
    qr = qrcode.make('http://paypal-verify.xyz/login')
    qr.save(os.path.join(output_dir, 'phishing_url.png'))
    
    # 3. Non-URL text QR
    qr = qrcode.make('Hello World - this is plain text, not a URL')
    qr.save(os.path.join(output_dir, 'plain_text.png'))
    
    # 4. Small QR (low version)
    qr_small = qrcode.QRCode(version=1, box_size=2, border=1)
    qr_small.add_data('https://example.com')
    qr_small.make(fit=True)
    img_small = qr_small.make_image(fill_color='black', back_color='white')
    img_small.save(os.path.join(output_dir, 'small_qr.png'))
    
    # 5. Low-contrast QR (gray on light gray)
    qr_lc = qrcode.QRCode(version=1, box_size=10, border=4)
    qr_lc.add_data('https://example.com/low-contrast')
    qr_lc.make(fit=True)
    img_lc = qr_lc.make_image(fill_color=(80, 80, 80), back_color=(200, 200, 200)).convert('RGB')
    img_lc.save(os.path.join(output_dir, 'low_contrast.png'))
    
    # 6. Create a blank image (no QR code) for negative test
    blank = Image.new('RGB', (100, 100), 'white')
    blank.save(os.path.join(output_dir, 'no_qr.png'))
    
    print(f'Generated {len(os.listdir(output_dir))} test QR images in {output_dir}')

if __name__ == '__main__':
    generate_test_qr_images()
