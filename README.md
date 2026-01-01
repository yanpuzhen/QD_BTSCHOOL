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

### 1. 拉取脚本 (三种方式)

#### 方式 A: 青龙订阅 (推荐)
在青龙面板的 **“订阅管理”** -> **“新建订阅”** 中输入：

**命令/脚本地址**:
```bash
ql repo https://github.com/yanpuzhen/QD_BTSCHOOL.git "signin" "" "requirements" "main"
```
**定时规则**: `0 9 * * *` (建议每天运行一次)

#### 方式 B: 手动添加
将本分支的 `signin.py` 和 `requirements.txt` 手动复制到青龙脚本库目录。

### 2. 依赖安装

#### 必须步骤：修复库缺失报错 (TargetClosedError / libglib missing)
因为青龙容器可能是 Alpine 或 Debian/Ubuntu 基础镜像，缺少 Chromium 运行所需的库。**请根据您的系统类型安装依赖：**

**情况 A: Alpine Linux (标准青龙容器)**
```bash
apk add chromium chromium-chromedriver udev ttf-freefont
```

**情况 B: Debian/Ubuntu (及部分第三方定制青龙)**
如果您的系统有 `apt` 或 `dpkg`，请运行：
```bash
# 1. 修复可能中断的安装
dpkg --configure -a

# 2. 安装依赖
apt-get update
# 推荐直接使用 playwright 自带的安装命令:
playwright install-deps chromium
# 或者手动安装:
apt-get install -y libglib2.0-0 libnss3 libnspr4 libatk1.0-0 libatk-bridge2.0-0 libcups2 libdrm2 libxkbcommon0 libxcomposite1 libxdamage1 libxfixes3 libxrandr2 libgbm1 libasound2
```

#### Python 依赖
- Python3 依赖: `playwright`, `google-genai`, `requests`, `pillow`
- 系统依赖: 确保上面的 Linux 库已安装即正常。

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
