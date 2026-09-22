import os
import time
from playwright.sync_api import sync_playwright

OUTPUT_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "demo_media")
os.makedirs(OUTPUT_DIR, exist_ok=True)

print("=" * 60)
print("  RECORDING CYBERSHIELD DEMO VIDEO & SCREENSHOTS")
print("=" * 60)

with sync_playwright() as p:
    browser = p.chromium.launch(headless=True)
    context = browser.new_context(
        viewport={"width": 1280, "height": 820},
        record_video_dir=OUTPUT_DIR,
        record_video_size={"width": 1280, "height": 820}
    )
    
    page = context.new_page()
    
    print("\n[Step 1] Navigating to CyberShield Desktop Application...")
    page.goto("http://localhost:8000", wait_until="networkidle")
    time.sleep(2)
    page.screenshot(path=os.path.join(OUTPUT_DIR, "01_desktop_home.png"))
    print("  Captured: 01_desktop_home.png")

    print("\n[Step 2] Testing Demo Preset 1: Digital Arrest Scam...")
    # Click the Digital Arrest preset button
    digital_arrest_btn = page.locator("button:has-text('Digital Arrest Scam')")
    if digital_arrest_btn.count() > 0:
        digital_arrest_btn.first.click()
        time.sleep(1)
        # Click Scan button
        scan_btn = page.locator("button:has-text('Scan with AI Guard')")
        if scan_btn.count() > 0:
            scan_btn.first.click()
            time.sleep(3)
            page.screenshot(path=os.path.join(OUTPUT_DIR, "02_digital_arrest_detected.png"))
            print("  Captured: 02_digital_arrest_detected.png")

    print("\n[Step 3] Testing Demo Preset 2: Bank Phishing Link...")
    phishing_btn = page.locator("button:has-text('Bank Phishing Link')")
    if phishing_btn.count() > 0:
        phishing_btn.first.click()
        time.sleep(1)
        scan_btn = page.locator("button:has-text('Scan with AI Guard')")
        if scan_btn.count() > 0:
            scan_btn.first.click()
            time.sleep(3)
            page.screenshot(path=os.path.join(OUTPUT_DIR, "03_bank_phishing_detected.png"))
            print("  Captured: 03_bank_phishing_detected.png")

    print("\n[Step 4] Testing Demo Preset 4: Legitimate Bank OTP...")
    otp_btn = page.locator("button:has-text('Legitimate Bank OTP')")
    if otp_btn.count() > 0:
        otp_btn.first.click()
        time.sleep(1)
        scan_btn = page.locator("button:has-text('Scan with AI Guard')")
        if scan_btn.count() > 0:
            scan_btn.first.click()
            time.sleep(3)
            page.screenshot(path=os.path.join(OUTPUT_DIR, "04_legitimate_otp_safe.png"))
            print("  Captured: 04_legitimate_otp_safe.png")

    print("\n[Step 5] Navigating to Performance & NPU Benchmark Tab...")
    perf_link = page.locator("a:has-text('Performance & NPU')")
    if perf_link.count() > 0:
        perf_link.first.click()
        time.sleep(2)
        page.screenshot(path=os.path.join(OUTPUT_DIR, "05_performance_benchmarks.png"))
        print("  Captured: 05_performance_benchmarks.png")

    print("\n[Step 6] Navigating to Scan History...")
    history_link = page.locator("a:has-text('History')")
    if history_link.count() > 0:
        history_link.first.click()
        time.sleep(2)
        page.screenshot(path=os.path.join(OUTPUT_DIR, "06_scan_history.png"))
        print("  Captured: 06_scan_history.png")

    # Closing context flushes and finalizes video recording
    context.close()
    browser.close()

# Find the recorded video file and rename it
video_files = [f for f in os.listdir(OUTPUT_DIR) if f.endswith(".webm")]
if video_files:
    latest_video = os.path.join(OUTPUT_DIR, video_files[0])
    target_video = os.path.join(OUTPUT_DIR, "cybershield_demo_walkthrough.webm")
    if os.path.exists(target_video):
        os.remove(target_video)
    os.rename(latest_video, target_video)
    size_mb = os.path.getsize(target_video) / (1024 * 1024)
    print(f"\nVIDEO DEMO SAVED: {target_video} ({size_mb:.2f} MB)")
else:
    print("\nNo video file found in output dir.")

print("=" * 60)
print("  RECORDING COMPLETED SUCCESSFULLY!")
print("=" * 60)
