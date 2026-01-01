# BTSchool 自动签到脚本 (Project Root)

这是一个用于 BTSchool (学校PT) 自动签到的 Python 脚本。它使用 `playwright` 模拟浏览器登录，并调用 **Google Gemini Vision API** 自动识别图形验证码。

本项目提供两种部署分支，请根据您的需求切换分支使用：

## 分支说明

### 1. [main 分支 (当前)](https://github.com/yanpuzhen/QD_BTSCHOOL/tree/main)
> **适用于：青龙面板 (QingLong Panel)、Docker、本地 Cron 任务**

- 适配青龙面板的环境变量配置。
- **重要特性**：包含 0-60 分钟随机启动延时，防止风控。
- **安全警告**：在青龙面板中请务必将“失败重试”设为 0。

### 2. [github-action 分支](https://github.com/yanpuzhen/QD_BTSCHOOL/tree/github-action)
> **适用于：GitHub Actions (云端自动运行)**

- 包含 `.github/workflows` 配置文件。
- 每天北京时间 09:00 自动运行。
- 通过 GitHub Secrets 管理密码和 Key。

---

## 青龙面板使用主要 (Main 分支)

### 1. 拉取脚本
将本分支的 `signin.py` 和 `requirements.txt` 添加到青龙脚本库。

### 2. 依赖安装
- Python3 依赖: `playwright`, `google-generativeai`, `requests`, `pillow`
- 系统依赖: `playwright install chromium` (需在容器内执行)

### 3.环境变量 (Environment Variables)

| 变量名 | 必填 | 说明 |
| :--- | :--- | :--- |
| `BTSCHOOL_USERNAME` | ✅ | 用户名 |
| `BTSCHOOL_PASSWORD` | ✅ | 密码 |
| `GEMINI_API_KEY` | ✅ | Google Gemini API Key |
| `GEMINI_MODEL_NAME` | ❌ | 模型 (默认 `gemini-2.0-flash-exp`) |
| `DINGTALK_WEBHOOK` | ❌ | 钉钉 Webhook |
| `DINGTALK_SECRET` | ❌ | 钉钉 Secret |

### ⚠️ 安全提示
**请务必将青龙面板任务的【失败重试次数】设置为 `0`！**
切勿配置自动重试，以免短时间多次尝试被封 IP。
