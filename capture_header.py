import os
import time
from playwright.sync_api import sync_playwright

output_dir = "demo_media"
os.makedirs(output_dir, exist_ok=True)

with sync_playwright() as p:
    browser = p.chromium.launch(headless=True)
    page = browser.new_page(viewport={"width": 1280, "height": 820})
    page.goto("http://localhost:8000", wait_until="networkidle")
    time.sleep(1)
    
    # 1. Capture dedicated header crop
    header = page.locator("header")
    header.screenshot(path=os.path.join(output_dir, "header_badge_preview.png"))
    print("Captured header_badge_preview.png")

    # 2. Update home screenshot
    page.screenshot(path=os.path.join(output_dir, "01_desktop_home.png"))
    print("Captured 01_desktop_home.png")

    # 3. Update digital arrest screenshot
    da_btn = page.locator("button:has-text('Digital Arrest Scam')")
    if da_btn.count() > 0:
        da_btn.first.click()
        time.sleep(0.5)
        scan_btn = page.locator("button:has-text('Scan with AI Guard')")
        if scan_btn.count() > 0:
            scan_btn.first.click()
            time.sleep(2)
            page.screenshot(path=os.path.join(output_dir, "02_digital_arrest_detected.png"))
            print("Captured 02_digital_arrest_detected.png")

    browser.close()
print("Done!")
