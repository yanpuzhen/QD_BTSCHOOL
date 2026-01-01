import os
import time
import random
import requests
import hmac
import hashlib
import base64
import urllib.parse
from playwright.sync_api import sync_playwright
from google import genai
import PIL.Image

# Load environment variables
# load_dotenv() # Removed for QingLong Panel usage (uses system env vars)

USERNAME = os.getenv("BTSCHOOL_USERNAME")
PASSWORD = os.getenv("BTSCHOOL_PASSWORD")
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
GEMINI_MODEL_NAME = os.getenv("GEMINI_MODEL_NAME", "gemini-2.0-flash-exp")

def send_dingtalk_msg(msg_content):
    webhook = os.getenv("DINGTALK_WEBHOOK")
    secret = os.getenv("DINGTALK_SECRET")
    
    if not webhook or not secret or webhook == "your_dingtalk_webhook":
        print("DINGTALK config missing or default. Skipping notification.")
        print(f"Would have sent: {msg_content}")
        return

    timestamp = str(round(time.time() * 1000))
    secret_enc = secret.encode('utf-8')
    string_to_sign = '{}\n{}'.format(timestamp, secret)
    string_to_sign_enc = string_to_sign.encode('utf-8')
    hmac_code = hmac.new(secret_enc, string_to_sign_enc, digestmod=hashlib.sha256).digest()
    sign = urllib.parse.quote_plus(base64.b64encode(hmac_code))

    url = f"{webhook}&timestamp={timestamp}&sign={sign}"
    
    headers = {'Content-Type': 'application/json'}
    data = {
        "msgtype": "text",
        "text": {
            "content": f"BTSchool 签到: {msg_content}"
        }
    }
    
    try:
        resp = requests.post(url, json=data, headers=headers)
        print(f"DingTalk response: {resp.text}")
    except Exception as e:
        print(f"Error sending DingTalk msg: {e}")

def run():
    with sync_playwright() as p:
        print("Launching browser...")
        browser = p.chromium.launch(headless=True)
        page = browser.new_page()
        
        try:
            print(f"Navigating to https://pt.btschool.club/login.php ...")
            page.goto("https://pt.btschool.club/login.php")
            
            # Step 1: Fill Username and Password
            print("Locating username field...")
            page.fill('input[name="username"]', USERNAME or "demo_user")
            
            print("Locating password field...")
            page.fill('input[name="password"]', PASSWORD or "demo_pass")
            
            print("Credentials filled.")
            
            # Step 2: Handle CAPTCHA
            print("Locating CAPTCHA image...")
            captcha_img = page.locator('img[src^="image.php"]')
            
            if captcha_img.count() > 0:
                print("CAPTCHA image found. Capturing...")
                captcha_path = "captcha.png"
                captcha_img.screenshot(path=captcha_path)
                
                # Call Gemini API
                if GEMINI_API_KEY and GEMINI_API_KEY != "your_gemini_api_key":
                    print("Configuring Gemini API (v2 SDK)...")
                    client = genai.Client(api_key=GEMINI_API_KEY)
                    
                    try:
                        print(f"Sending image to Gemini model ({GEMINI_MODEL_NAME})...")
                        img = PIL.Image.open(captcha_path)
                        response = client.models.generate_content(
                            model=GEMINI_MODEL_NAME,
                            contents=["Return only the characters visible in the image, no other text.", img]
                        )
                        captcha_text = response.text.strip()
                        print(f"Gemini Predicted CAPTCHA: '{captcha_text}'")
                        
                        # Fill the CAPTCHA field
                        print("Filling CAPTCHA field...")
                        page.fill('input[name="imagestring"]', captcha_text)
                        
                        # Step 3: Click Login
                        print("Clicking 'Login' button...")
                        page.click('input[type="submit"].btn')
                        
                        # Wait for login result
                        print("Waiting 10 seconds for initial load...")
                        page.wait_for_timeout(10000)
                        
                        # Take detailed screenshot of the result
                        result_path = "login_result.png"
                        print("Taking screenshot (timeout: 120s)...")
                        try:
                            page.screenshot(path=result_path, full_page=True, timeout=120000)
                            print(f"Login attempt finished. Screenshot saved to {result_path}")
                        except Exception as e:
                            print(f"Screenshot timed out or failed: {e}")
                        
                        print(f"Current URL: {page.url}")

                        # Step 4: Bonus Collection
                        print("Navigating to Bonus Page...")
                        page.goto("https://pt.btschool.club/index.php?action=addbonus")
                        
                        print("Waiting 30 seconds as requested...")
                        time.sleep(30)
                        
                        # Extract bonus text
                        print("Extracting bonus info...")
                        try:
                            # Try precise selector: <font color="white">...今天签到您获得...</font>
                            # Using XPath to be safer with text content
                            bonus_element = page.locator('//font[@color="white"][contains(text(),"今天签到")]')
                            
                            if bonus_element.count() > 0:
                                bonus_text = bonus_element.first.inner_text()
                                bonus_text = bonus_element.first.inner_text()
                                print(f"找到签到信息: {bonus_text}")
                                send_dingtalk_msg(f"签到成功，{bonus_text}")
                            else:
                                # Fallback: look for the green cell or "Already signed in" text?
                                print("Primary selector failed. Checking for 'already signed in' or other states...")
                                
                                # Check if page text contains "已签到"
                                body_text = page.inner_text("body")
                                if "已签到" in body_text or "已经签到" in body_text:
                                if "已签到" in body_text or "已经签到" in body_text:
                                    print("检测到 '已签到' 状态。")
                                    send_dingtalk_msg("签到成功 (今日已签)")
                                else:
                                    print("尝试备用绿色单元格选择器...")
                                    td_locator = page.locator('td[style*="background: green"]')
                                    if td_locator.count() > 0:
                                         bonus_text = td_locator.first.inner_text().strip()
                                         print(f"找到魔力值信息 (备用): {bonus_text}")
                                         send_dingtalk_msg(f"签到成功，获得: {bonus_text}")
                                    else:
                                        print("未找到签到信息，正在截图...")
                                        page.screenshot(path="bonus_debug.png", full_page=True)
                                        send_dingtalk_msg("登录成功，但未提取到魔力值。请检查日志或截图 (bonus_debug.png)")
                                    
                        except Exception as e:
                            print(f"Error extracting bonus: {e}")
                            page.screenshot(path="bonus_error.png")
                            send_dingtalk_msg(f"Login successful, error checking bonus: {e}")

                    except Exception as e:
                        print(f"ERROR calling Gemini API/Login Flow: {e}")
                else:
                    print("WARNING: GEMINI_API_KEY not set or is default. Awaiting user configuration.")
            else:
                print("ERROR: CAPTCHA image not found!")
                
        except Exception as e:
            print(f"Script Error: {e}")
        finally:
            print("Script finished.")
            browser.close()

if __name__ == "__main__":
    run()
