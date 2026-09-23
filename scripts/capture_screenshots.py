import os
import time
from playwright.sync_api import sync_playwright

output_dir = "demo_media"
os.makedirs(output_dir, exist_ok=True)

with sync_playwright() as p:
    browser = p.chromium.launch(headless=True)
    page = browser.new_page(viewport={"width": 1280, "height": 820})
    
    # 1. Desktop Home
    page.goto("http://localhost:8000", wait_until="networkidle")
    time.sleep(1)
    page.screenshot(path=os.path.join(output_dir, "01_desktop_home.png"))
    print("Captured 01_desktop_home.png")

    # 2. Digital Arrest Scam
    da_btn = page.locator("button:has-text('Digital Arrest Scam')")
    if da_btn.count() > 0:
        da_btn.first.click()
        time.sleep(0.5)
        scan_btn = page.locator("button:has-text('Scan with AI Guard')")
        if scan_btn.count() > 0:
            scan_btn.first.click()
            time.sleep(2.5)
            page.screenshot(path=os.path.join(output_dir, "02_digital_arrest_detected.png"))
            print("Captured 02_digital_arrest_detected.png")

    # 3. Bank Phishing
    phish_btn = page.locator("button:has-text('Bank Phishing Link')")
    if phish_btn.count() > 0:
        phish_btn.first.click()
        time.sleep(0.5)
        scan_btn = page.locator("button:has-text('Scan with AI Guard')")
        if scan_btn.count() > 0:
            scan_btn.first.click()
            time.sleep(2.5)
            page.screenshot(path=os.path.join(output_dir, "03_bank_phishing_detected.png"))
            print("Captured 03_bank_phishing_detected.png")

    # 4. History tab
    history_link = page.locator("a:has-text('History')")
    if history_link.count() > 0:
        history_link.first.click()
        time.sleep(2)
        page.screenshot(path=os.path.join(output_dir, "06_scan_history.png"))
        print("Captured 06_scan_history.png")

    # 5. Performance tab
    perf_link = page.locator("a:has-text('Performance & NPU')")
    if perf_link.count() > 0:
        perf_link.first.click()
        time.sleep(2)
        page.screenshot(path=os.path.join(output_dir, "05_performance_benchmarks.png"))
        print("Captured 05_performance_benchmarks.png")

    browser.close()

print("ALL UPDATED SCREENSHOTS SAVED.")
