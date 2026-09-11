# 我的 Codex Skill 与插件一键恢复包

这个仓库保存我的个人 Codex skill，并记录这台电脑正在使用的 Codex 插件。换电脑后，可以让 Codex 根据本说明自动恢复，也可以在 PowerShell 中手动运行安装脚本。

仓库地址：<https://github.com/yangaobo0235/my-codex-skills>

## 推荐方式：让新电脑上的 Codex 自动恢复

先在新电脑完成以下准备：

1. 安装并启动 Codex。
2. 至少启动一次 Codex 桌面版，让官方内置插件和文档运行时完成初始化。
3. 登录 GitHub，并确认当前账号有权访问这个私有仓库。
4. 打开一个新的 Codex 对话。

然后把下面这段话连同仓库链接发送给 Codex：

```text
请恢复这个仓库清单中的全部个人 skill 和插件：
https://github.com/yangaobo0235/my-codex-skills

请先阅读仓库根目录的 README.md 和 skills-manifest.json，再按 README 的说明执行 install.ps1。
安装前先运行检查模式；确认范围后安装全部个人 skill 和清单中的插件。
如果 openai-bundled 或 openai-primary-runtime 尚未注册，请让脚本从当前 Codex 桌面版和官方主运行时中自动发现并注册。
请只安装 skills-manifest.json 的 plugins 数组列出的插件，不安装或替换清单以外的插件。
不要上传或输出任何 Token、密码、账户授权、本机配置或绝对路径。
安装完成后验证结果，并告诉我是否需要重启 Codex。
```

Codex 会读取仓库里的 `README.md`、`skills-manifest.json` 和 `install.ps1`，然后把个人 skill 安装到当前用户的 Codex skill 目录，并补齐清单中缺失的插件。脚本会自动发现当前 Codex 桌面版附带的 `openai-bundled` 市场，以及文档主运行时附带的 `openai-primary-runtime` 市场。安装完成后重启 Codex，新能力会在下一次会话中生效。

## 备用方式：手动安装

如果新电脑上的 Codex 没有自动执行命令，可以在 PowerShell 中运行：

```powershell
git clone https://github.com/yangaobo0235/my-codex-skills.git
Set-Location .\my-codex-skills

# 第一步：只检查，不修改电脑
powershell -ExecutionPolicy Bypass -File .\install.ps1 -Check

# 第二步：安装个人 skill 和缺失插件
powershell -ExecutionPolicy Bypass -File .\install.ps1
```

只安装个人 skill、不安装插件：

```powershell
powershell -ExecutionPolicy Bypass -File .\install.ps1 -SkipPlugins
```

指定自定义 Codex 目录（以下使用相对目录示例）：

```powershell
powershell -ExecutionPolicy Bypass -File .\install.ps1 -CodexHomePath '.\codex-home'
```

## 安装行为

- 个人 skill 安装到 `$CODEX_HOME\skills`；未设置 `CODEX_HOME` 时使用 `%USERPROFILE%\.codex\skills`。
- 已存在的 skill 不会覆盖，避免破坏新电脑上已有内容。
- 缺少 `openai-bundled` 或 `openai-primary-runtime` 时，脚本会从当前 Codex 官方桌面包或主运行时自动发现并注册。
- 已安装的插件会自动跳过，脚本可以重复运行。
- `-Check` 模式不会创建目录、复制文件或安装插件。
- 安装结束会重新读取插件清单，确认 11 个插件全部存在。
- 安装后需要重启 Codex。

## 本仓库包含什么

### 个人 skill

- `backend-interview-simulator`：Java、C++、Go、AI 应用和混合技术栈的后端面试模拟
- `kwai`：AI 应用经验上传助手
- `run-interview-note-defense`：多角色、多轮面试攻防与面试笔记重写
- `write-engineering-resume`：基于技术事实和证据改写工程师简历
- `write-interview-notes`：整理、合并和审查中文技术面试笔记

### 插件

`skills-manifest.json` 记录以下 11 个插件：

- `computer-use`：控制 Windows 桌面应用
- `documents`：创建和编辑 Word 文档
- `pdf`：读取、创建和检查 PDF
- `presentations`：创建和编辑 PowerPoint 演示文稿
- `spreadsheets`：创建、分析和编辑表格，并支持实时 Excel 控制
- `template-creator`：制作可复用的个人文档模板
- `visualize`：创建图表、地图、流程图和交互式可视化
- `browser`：控制 Codex 内置浏览器
- `chrome`：控制带有现有登录状态的 Chrome
- `codex-app-tools`：提供 Codex 桌面端工具
- `unified-computer-use`：提供浏览器自动化运行时

`plugins` 数组是安装白名单；脚本只安装其中列出的插件，不处理清单以外的插件。插件由当前 Codex 官方桌面包或主运行时提供，仓库不保存插件缓存。

Codex 自带的 `imagegen`、`openai-docs`、`plugin-creator`、`review-agent`、`skill-creator` 和 `skill-installer` 不需要复制源码。

## 前置条件与常见问题

### 私有仓库无法克隆

先确认新电脑已登录 GitHub，并且该账号被授予仓库访问权限。也可以先在 PowerShell 中单独运行：

```powershell
git ls-remote https://github.com/yangaobo0235/my-codex-skills.git
```

### 插件安装失败

确认新电脑已经安装并至少启动过一次最新版 Codex 桌面版。可以先运行：

```powershell
codex plugin marketplace list
codex plugin list --json
```

然后再次运行 `install.ps1`。脚本只会注册清单所需的官方本地市场并补装缺失插件。如果仍提示找不到 `openai-primary-runtime`，请先重启 Codex，让主运行时完成下载后再重试。

### skill 已经存在

这是保护行为，不是错误。脚本会保留已有目录；如果需要用仓库版本覆盖，请先手动备份并删除对应目录，再重新运行安装脚本。

## 安全说明

本仓库不保存 API Token、密码、GitHub 登录信息、Slack/Google 授权、本机 `config.toml`、插件缓存或任何本机绝对路径。私有仓库权限仍应按 GitHub 的正常方式管理。
