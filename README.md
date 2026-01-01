# BTSchool 自动签到脚本 (GitHub Action 版)

这是一个用于 BTSchool (学校PT) 自动签到的 Python 脚本。它使用 `playwright` 模拟浏览器登录，并调用 **Google Gemini Vision API** 自动识别图形验证码。

**本分支 (`github-action`) 专为 GitHub Actions 自动运行优化。**

## 功能列表

- ✅ **自动定时运行**：每天北京时间 09:00 自动执行。
- ✅ **智能识别验证码**：使用 Gemini 模型识别验证码。
- ✅ **随机延时**：脚本内建 0-60 分钟随机等待。
- ✅ **钉钉推送**：支持钉钉机器人通知。

## 部署说明

### 1. Fork 本仓库
点击右上角的 **Fork** 按钮，将本仓库复制到你的账号下。

### 2. 配置 Secrets
进入你的仓库，点击 **Settings** -> **Secrets and variables** -> **Actions** -> **New repository secret**，添加以下变量：

| Secret Name | 必填 | 说明 |
| :--- | :--- | :--- |
| `BTSCHOOL_USERNAME` | ✅ | BTSchool 的登录用户名 |
| `BTSCHOOL_PASSWORD` | ✅ | BTSchool 的登录密码 |
| `GEMINI_API_KEY` | ✅ | Google Gemini API Key ([申请地址](https://aistudio.google.com/app/apikey)) |
| `DINGTALK_WEBHOOK` | ❌ | 钉钉群机器人 Webhook 地址 |
| `DINGTALK_SECRET` | ❌ | 钉钉群机器人加签密钥 |

*(可选)* 如果需要更改模型名称（默认 `gemini-2.0-flash-exp`），可以在 **Variables** 标签页添加 `GEMINI_MODEL_NAME`。

### 3. 启用 Workflow
进入 **Actions** 标签页，点击左侧的 "BTSchool Daily Sign-in"，如果原本被禁用，点击 **Enable workflow**。

你也可以点击 **Run workflow** -> **Run workflow** 手动触发一次测试。

---
**注意**：GitHub Action 的 IP 可能会变动，如果 PT 站对 IP 变动敏感，请谨慎使用或通过自建 Runner 解决。
