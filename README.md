# 我的 Codex Skills 一键恢复包

这个仓库保存我的个人 Codex skill，并记录这台电脑正在使用的 Codex 插件。换电脑后，可以让 Codex 根据本说明自动恢复，也可以在 PowerShell 中手动运行安装脚本。

仓库地址：<https://github.com/yangaobo0235/my-codex-skills>

## 推荐方式：让新电脑上的 Codex 自动恢复

先在新电脑完成以下准备：

1. 安装并启动 Codex。
2. 登录 GitHub，并确认当前账号有权访问这个私有仓库。
3. 打开一个新的 Codex 对话。

然后把下面这段话连同仓库链接发送给 Codex：

```text
请恢复这个仓库中的全部 Codex skill 和插件：
https://github.com/yangaobo0235/my-codex-skills

请先阅读仓库根目录的 README.md 和 skills-manifest.json，再按 README 的说明执行 install.ps1。
安装前先运行检查模式；确认范围后安装全部个人 skill 和清单中的插件。
不要上传或输出任何 Token、密码、账户授权、本机配置或绝对路径。
安装完成后验证结果，并告诉我是否需要重启 Codex。
```

Codex 会读取仓库里的 `README.md`、`skills-manifest.json` 和 `install.ps1`，然后把个人 skill 安装到当前用户的 Codex skill 目录，并补齐清单中缺失的插件。安装完成后重启 Codex，新 skill 会在下一次会话中生效。

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

指定自定义 Codex 目录：

```powershell
powershell -ExecutionPolicy Bypass -File .\install.ps1 -CodexHomePath 'D:\\CodexHome'
```

## 安装行为

- 个人 skill 安装到 `$CODEX_HOME\skills`；未设置 `CODEX_HOME` 时使用 `%USERPROFILE%\.codex\skills`。
- 已存在的 skill 不会覆盖，避免破坏新电脑上已有内容。
- 已安装的插件会自动跳过，脚本可以重复运行。
- `-Check` 模式不会创建目录、复制文件或安装插件。
- 安装后需要重启 Codex。

## 本仓库包含什么

### 个人 skill

- `backend-interview-simulator`：Java、C++、Go、AI 应用和混合技术栈的后端面试模拟
- `kwai`：AI 应用经验上传助手
- `run-interview-note-defense`：多角色、多轮面试攻防与面试笔记重写
- `write-engineering-resume`：基于技术事实和证据改写工程师简历
- `write-interview-notes`：整理、合并和审查中文技术面试笔记

### 插件

`skills-manifest.json` 记录了当前使用的文档、PDF、表格、PPT、浏览器、电脑操作、可视化和 Superpowers 插件。插件由 Codex 官方市场或运行时重新下载，仓库不复制插件缓存。

Codex 自带的 `imagegen`、`openai-docs`、`plugin-creator`、`skill-creator` 和 `skill-installer` 不需要复制源码。

## 前置条件与常见问题

### 私有仓库无法克隆

先确认新电脑已登录 GitHub，并且该账号被授予仓库访问权限。也可以先在 PowerShell 中单独运行：

```powershell
git ls-remote https://github.com/yangaobo0235/my-codex-skills.git
```

### 插件安装失败

确认新电脑已经安装最新版 Codex，并且 Codex 能正常访问插件市场。可以先运行：

```powershell
codex plugin marketplace list
codex plugin list --json
```

然后再次运行 `install.ps1`。脚本只会补装缺失插件。

### skill 已经存在

这是保护行为，不是错误。脚本会保留已有目录；如果需要用仓库版本覆盖，请先手动备份并删除对应目录，再重新运行安装脚本。

## 安全说明

本仓库不保存 API Token、密码、GitHub 登录信息、Slack/Google 授权、本机 `config.toml`、插件缓存或任何本机绝对路径。私有仓库权限仍应按 GitHub 的正常方式管理。
