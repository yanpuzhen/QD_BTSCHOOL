# BTSchool 自动签到脚 (GitHub Action 版)

本分支 (`github-action`) 专为 GitHub Actions 云端自动运行优化。

如果您需要青龙面板版本，请切换到 [main 分支](https://github.com/yanpuzhen/QD_BTSCHOOL/tree/main)。

---

## GitHub Action 版本特性

- ✅ **自动定时**：每天北京时间 09:00 (UTC 01:00) 自动执行。
- ✅ **环境集成**：无需自建服务器，利用 GitHub 免费 Runner 运行。
- ✅ **随机延时**：保留脚本内部的 0-60 分钟随机等待，模拟真人。

## 部署步骤

### 1. Fork 仓库
点击右上角的 **Fork** 按钮，将本仓库复制到你的 GitHub 账号下。

### 2. 启用 Actions
进入 Fork 后的仓库，点击顶部的 **Actions** 标签页。
如果看到 "Workflows aren't being run on this forked repository"，请点击绿色的 **I understand my workflows, go ahead and enable them** 按钮。

### 3. 配置 Secrets (关键)
进入 **Settings** -> **Secrets and variables** -> **Actions** -> **New repository secret**，添加以下变量：

| Secret Name | 必填 | 说明 |
| :--- | :--- | :--- |
| `BTSCHOOL_USERNAME` | ✅ | BTSchool 用户名 |
| `BTSCHOOL_PASSWORD` | ✅ | BTSchool 密码 |
| `GEMINI_API_KEY` | ✅ | Google Gemini API Key |
| `DINGTALK_WEBHOOK` | ❌ | 钉钉 Webhook |
| `DINGTALK_SECRET` | ❌ | 钉钉 Secret |

### 4. 手动测试
配置完成后，回到 **Actions** 标签页，在左侧选择 "BTSchool Daily Sign-in"，点击右侧的 **Run workflow** 按钮进行测试。

---
**注意**：GitHub Action 的出口 IP 不固定。如果站点对异地登录非常敏感，请谨慎使用。
