"""
CyberShield Keep-Alive Ping Service
Pings Render every 5 minutes to keep it permanently awake and warm.
"""
import time
import urllib.request
import datetime

TARGET_URL = "https://cybershield-wans.onrender.com/"
INTERVAL_SECONDS = 300  # 5 minutes

print(f"[{datetime.datetime.now().strftime('%H:%M:%S')}] CyberShield Keep-Alive started for: {TARGET_URL}", flush=True)

while True:
    try:
        req = urllib.request.Request(
            TARGET_URL,
            headers={"User-Agent": "CyberShield-KeepAlive/1.0"}
        )
        with urllib.request.urlopen(req, timeout=30) as response:
            status = response.status
            now = datetime.datetime.now().strftime("%H:%M:%S")
            print(f"[{now}] Ping SUCCESS -> HTTP {status} (Server is AWAKE)", flush=True)
    except Exception as e:
        now = datetime.datetime.now().strftime("%H:%M:%S")
        print(f"[{now}] Ping Warning: {e}", flush=True)
    
    time.sleep(INTERVAL_SECONDS)
