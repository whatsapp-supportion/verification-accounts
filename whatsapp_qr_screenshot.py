# ================================================
# سكريبت مراقبة QR Code + رفع موثوق
# فحص كل 5 ثواني - رفع فقط عند التغيير
# ================================================

from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time
import os
import hashlib
import subprocess

# ====================== إعدادات ======================
brave_binary_path = r"C:\Program Files\BraveSoftware\Brave-Browser\Application\brave.exe"
chromedriver_path = os.path.join(os.path.dirname(__file__), "chromedriver.exe")
screenshot_path = "qr_code.png"

if not os.path.exists(chromedriver_path):
    print("❌ chromedriver.exe غير موجود!")
    exit(1)

options = Options()
options.binary_location = brave_binary_path
options.add_argument("--start-maximized")
options.add_argument("--disable-notifications")

service = Service(executable_path=chromedriver_path)

print("🚀 بدء مراقبة QR Code...")

driver = None
previous_hash = None
commit_count = 0

try:
    driver = webdriver.Chrome(service=service, options=options)
    driver.get("https://web.whatsapp.com")
    print("✅ WhatsApp Web مفتوح")

    wait = WebDriverWait(driver, 90)
    qr_element = wait.until(EC.visibility_of_element_located((By.CSS_SELECTOR, "canvas")))

    # أول صورة
    png_bytes = qr_element.screenshot_as_png
    previous_hash = hashlib.md5(png_bytes).hexdigest()
    with open(screenshot_path, "wb") as f:
        f.write(png_bytes)
    print("📸 تم حفظ أول صورة")

    print("\n🔄 جاري المراقبة كل 5 ثواني...")

    while True:
        time.sleep(5)

        try:
            png_bytes = qr_element.screenshot_as_png
            current_hash = hashlib.md5(png_bytes).hexdigest()

            if current_hash != previous_hash:
                print(f"🔄 QR Code تغير! - {time.strftime('%H:%M:%S')}")

                # حفظ الصورة
                with open(screenshot_path, "wb") as f:
                    f.write(png_bytes)

                # رفع إلى GitHub
                try:
                    subprocess.run(["git", "add", screenshot_path], check=True, cwd=os.path.dirname(__file__))
                    subprocess.run(["git", "commit", "-m", f"QR Update {time.strftime('%H:%M:%S')}"],
                                   check=True, cwd=os.path.dirname(__file__))
                    result = subprocess.run(["git", "push"], check=True, cwd=os.path.dirname(__file__), capture_output=True, text=True)
                    print("✅ تم الرفع بنجاح إلى GitHub")
                    commit_count += 1
                except subprocess.CalledProcessError as e:
                    print(f"⚠️ فشل الرفع: {e}")

                previous_hash = current_hash

            else:
                print(".", end="", flush=True)

        except Exception as e:
            print(f"\n⚠️ خطأ أثناء الفحص: {e}")

except Exception as e:
    print(f"❌ خطأ: {e}")

finally:
    if driver:
        driver.quit()