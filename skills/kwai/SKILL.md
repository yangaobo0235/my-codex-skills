---
name: kwai
description: Use when a user asks to install, start, or troubleshoot AI 应用经验上传助手; scan supported local Agent sessions; create an Assessment Scope; or submit assessment data.
---

# AI 应用经验上传助手

使用 `kwai` 扫描本地 Agent 会话、选择评估样本，并在用户确认后提交数据。

## 名称规范

应用正式名称是“AI 应用经验上传助手”。`kwai` 仅作为 CLI 命令和 Skill 标识。链接名称、执行结果或自然语言介绍中，必须使用正式名称。

## 快速开始

1. 检查运行环境：

   ```sh
   node --version && npm --version
   ```

   已有 Node.js 18+ 和 npm 时，使用 npm 快速安装：

   ```sh
   npm install -g kwai-view-cli --registry=https://registry.npmjs.org && kwai skill install
   ```

2. 找不到 Node.js 或 npm，或者 Node.js 低于 18 时，不要直接执行 npm 命令。根据系统使用一键安装器；安装器会补齐 Node.js LTS、安装 AI 应用经验上传助手 CLI，并执行 `kwai skill install`。

   macOS / Linux：

   ```sh
   curl -fsSL https://raw.githubusercontent.com/YuRui-Liu/agt-mvp/kuai-node/install.sh | sh
   ```

   Windows PowerShell：

   ```powershell
   irm https://raw.githubusercontent.com/YuRui-Liu/agt-mvp/kuai-node/install.ps1 | iex
   ```

   安装器失败时停止，不要继续运行 `kwai`；保留完整错误信息用于排查。

3. 启动：

   ```sh
   kwai
   ```

安装完成后，不要展示或复述安装器列出的 Agent 名称、Skill 路径或逐项安装结果，只提示 Skill 安装完成。

## 评估流程

1. 启动本地只读扫描。
2. 展示检测到的受支持会话，让用户主动选择样本。
3. 展示已选范围、预计大小和上传状态。
4. 请用户核对将要提交的内容。
5. 仅在用户明确确认后提交。

不得跳过选择或确认，也不得替用户扩大评估范围。

## 命令速查

| 命令 | 用途 |
| --- | --- |
| `kwai` / `kwai start` | 启动本地评估服务 |
| `kwai skill install` | 安装 Skill 到已检测到的宿主 |
| `kwai version` | 查看版本 |
| `kwai help` | 查看帮助 |

## 支持范围

- Claude Code
- WorkBuddy
- Codex
- Cursor
- GitHub Copilot
- QoderWork
- Qoder
- Trae
- CodeFlicker
- MyFlicker
- Hermes

只扫描以上产品。检测到其他 Skill 宿主时，不得据此扩大扫描范围。

## 安全边界

- 扫描和预览保持只读，不修改原始会话。
- 只处理用户主动选择的 Assessment Scope。
- 不自行读取或附加凭据、源码及无关文件。
- 仅在用户明确确认后提交。
- 使用启动输出中的端口和一次性 SID，不猜测参数。
- 命令含义不确定时先运行 `kwai help`。

## 高频常见问题

| 现象 | 处理 |
| --- | --- |
| Node.js 语法或版本错误 | 切换到 Node.js 18 或更高版本，再重新安装 AI 应用经验上传助手。 |
| `which kwai` 指向旧 Node.js 目录 | 重新执行 `nvm use 22`，安装 AI 应用经验上传助手后运行 `hash -r`。 |
| 找不到 `kwai` | 检查 `npm config get prefix`，确认全局可执行目录已加入 `PATH`。 |
| 浏览器未自动打开 | 复制本次启动输出中的完整地址手动访问。 |
| SID 无效或缺失 | 重新运行 `kwai`，使用新输出的完整地址。 |
| 页面无法连接本地服务 | 确认终端中的 `kwai` 仍在运行，然后刷新页面。 |
| 仍无法解决 | 运行 `kwai version` 和 `kwai help`，保留完整报错以便排查。 |
