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
        print("钉钉配置缺失或为默认值。跳过发送通知。")
        print(f"本应发送内容: {msg_content}")
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
        print(f"钉钉接口响应: {resp.text}")
    except Exception as e:
        print(f"发送钉钉消息出错: {e}")

def run():
    with sync_playwright() as p:
        print("正在启动浏览器...")
        browser = p.chromium.launch(headless=True)
        page = browser.new_page()
        
        try:
            print(f"正在访问 https://pt.btschool.club/login.php ...")
            page.goto("https://pt.btschool.club/login.php")
            
            # Step 1: Fill Username and Password
            print("正在定位用户名输入框...")
            page.fill('input[name="username"]', USERNAME or "demo_user")
            
            print("正在定位密码输入框...")
            page.fill('input[name="password"]', PASSWORD or "demo_pass")
            
            print("账号密码已填充。")
            
            # 第 2 步：处理验证码
            print("正在定位验证码图片...")
            captcha_img = page.locator('img[src^="image.php"]')
            
            if captcha_img.count() > 0:
                print("找到验证码。正在截图...")
                captcha_path = "captcha.png"
                captcha_img.screenshot(path=captcha_path)
                
                # 调用 Gemini API
                if GEMINI_API_KEY and GEMINI_API_KEY != "your_gemini_api_key":
                    print("正在配置 Gemini API (v2 SDK)...")
                    client = genai.Client(api_key=GEMINI_API_KEY)
                    
                    try:
                        print(f"正在向 Gemini 模型 ({GEMINI_MODEL_NAME}) 发送请求...")
                        img = PIL.Image.open(captcha_path)
                        response = client.models.generate_content(
                            model=GEMINI_MODEL_NAME,
                            contents=["Return only the characters visible in the image, no other text.", img]
                        )
                        captcha_text = response.text.strip()
                        print(f"Gemini 识别到的验证码: '{captcha_text}'")
                        
                        # 填充验证码
                        print("正在填充验证码...")
                        page.fill('input[name="imagestring"]', captcha_text)
                        
                        # 第 3 步：点击登录
                        print("正在点击 '登录' 按钮...")
                        page.click('input[type="submit"].btn')
                        
                        # 等待登录结果
                        print("正在等待 10 秒以加载...")
                        page.wait_for_timeout(10000)
                        
                        # 截图登录结果
                        result_path = "login_result.png"
                        print("正在截图（超时时间：120秒）...")
                        try:
                            page.screenshot(path=result_path, full_page=True, timeout=120000)
                            print(f"登录尝试完成。截图已保存至 {result_path}")
                        except Exception as e:
                            print(f"截图超时或失败: {e}")
                        
                        print(f"当前 URL: {page.url}")

                        # Check if login was successful
                        if "login.php" in page.url:
                            print("登录失败：仍停留在登录页面。")
                            # Look for error message
                            error_msg = page.locator('.embedded table td.text').first.inner_text() if page.locator('.embedded table td.text').count() > 0 else "未知错误"
                            print(f"检测到错误: {error_msg}")
                            send_dingtalk_msg(f"登录失败: {error_msg}")
                            page.screenshot(path="login_failed.png")
                            return

                        # Final verification: Check for Logout link
                        if page.locator('a[href="logout.php"]').count() == 0:
                            print("登录结果不明确：未找到退出链接。")
                            # We'll still try to proceed but with a warning
                        else:
                            print("登录成功（已找到退出链接）。")

                        # 第 4 步：签到送魔力值
                        print("正在跳转至签到页面...")
                        page.goto("https://pt.btschool.club/index.php?action=addbonus")
                        
                        print("按要求等待 30 秒...")
                        time.sleep(30)
                        
                        # 提取签到信息
                        print("正在提取签到信息...")
                        try:
                            # Try precise selector: <font color="white">...今天签到您获得...</font>
                            # Using XPath to be safer with text content
                            bonus_element = page.locator('//font[@color="white"][contains(text(),"今天签到")]')
                            
                            if bonus_element.count() > 0:
                                bonus_text = bonus_element.first.inner_text()
                                print(f"找到签到信息: {bonus_text}")
                                send_dingtalk_msg(f"签到成功，{bonus_text}")
                            else:
                                # 备用方案：检查是否绿色单元格或“已签到”？
                                print("主要选择器失效。正在检查是否为‘已签到’或其他状态...")
                                
                                # Check if page text contains "已签到"
                                body_text = page.inner_text("body")
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
                            send_dingtalk_msg(f"登录成功，但在检查魔力值时发生错误: {e}")

                    except Exception as e:
                        print(f"调用 Gemini API 或登录流程出错: {e}")
                else:
                    print("警告: GEMINI_API_KEY 未设置或为默认值。请配置环境变量。")
            else:
                print("错误: 未找到验证码图片！")
                
        except Exception as e:
            print(f"脚本执行错误: {e}")
        finally:
            print("脚本运行结束。")
            browser.close()

if __name__ == "__main__":
    run()
