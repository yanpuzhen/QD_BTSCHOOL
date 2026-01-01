# BTSchool 自动签到脚 (学校PT)

这是一个用于 BTSchool (学校PT) 网站自动签到的 Python 脚本。它使用 `playwright` 模拟浏览器登录，并调用 **Google Gemini Vision API** 自动识别图形验证码。支持签到后获取魔力值提示，并通过钉钉机器人发送通知。

## 功能列表

- ✅ 自动模拟登录 `pt.btschool.club`
- ✅ **智能识别验证码**：使用 Gemini 可视化模型 (如 `gemini-2.0-flash-exp` 或 `gemini-1.5-flash`) 识别验证码，高准确率。
- ✅ **随机延时**：启动后随机等待 0-60 分钟，防止固定时间签到被风控。
- ✅ **钉钉推送**：签到结果和获得的魔力值通过钉钉群机器人 Webhook 推送。
- ✅ **错误重试/容错**：自动处理 API 配额不足（虽然脚本本身运行一次，建议配合青龙的重试机制）。

## 青龙面板使用主要

### 1. 拉取/添加脚本
将本仓库的 `signin.py` 和 `requirements.txt` 添加到你的青龙面板脚本库中。

### 2. 安装依赖
在青龙面板的依赖管理中，找到 **Python3** 依赖，添加以下包：
```
playwright
google-generativeai
requests
pillow
```
**注意**：Playwright 需要浏览器内核支持。如果你的青龙容器没有预装浏览器，你可能需要在“配置文件” -> `extra.sh` 中添加安装命令，或者直接在 Docker 宿主机安装。
通用方法是进入容器终端运行：
```bash
playwright install chromium
playwright install-deps chromium
```

### 3. 配置环境变量
在青龙面板的 **“环境变量”** (Environment Variables) 中添加以下变量：

| 变量名 | 必填 | 说明 |
| :--- | :--- | :--- |
| `BTSCHOOL_USERNAME` | ✅ | BTSchool 的登录用户名 |
| `BTSCHOOL_PASSWORD` | ✅ | BTSchool 的登录密码 |
| `GEMINI_API_KEY` | ✅ | Google Gemini API Key ([申请地址](https://aistudio.google.com/app/apikey)) |
| `GEMINI_MODEL_NAME` | ❌ | 模型名称，默认为 `gemini-2.0-flash-exp`，可选 `gemini-1.5-flash` |
| `DINGTALK_WEBHOOK` | ❌ | 钉钉群机器人 Webhook 地址（完整 URL） |
| `DINGTALK_SECRET` | ❌ | 钉钉群机器人的加签密钥 (SEC开头...) |

### 4. 运行
添加定时任务，例如每天早上 9 点运行：
```cron
0 9 * * * python3 /ql/scripts/your_script_path/signin.py
```
（因为脚本自带 0-60 分钟随机延时，设为每天固定时间触发即可，脚本会自动分散执行时间）

### ⚠️ 重要安全提示
**请务必将青龙面板任务的【失败重试次数】设置为 `0`！**
- 脚本本身只执行一次登录尝试。
- 如果因为网络或验证码错误导致失败，**切勿让青龙面板自动重试**。
- PT站对短时间内多次登录失败非常敏感，重试可能导致 IP 被封禁。

## 本地开发/调试

1. 安装依赖: `pip install -r requirements.txt`
2. 运行脚本: `python signin.py`
   (本地环境会自动读取环境变量，或你可以手动临时修改脚本中的 getenv 默认值进行测试)
