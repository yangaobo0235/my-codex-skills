# Codex Skills 备份

这个仓库保存我个人维护、可以跨电脑迁移的 Codex skills。每个 skill 都是一个独立目录，入口文件是该目录下的 `SKILL.md`。

## Skill 说明

| Skill | 用途 | 适用场景 |
| --- | --- | --- |
| `backend-interview-simulator` | 后端技术面试模拟器，支持 Java、C++、Go、AI 应用和混合技术栈面试 | 根据简历或职位描述进行面试，逐题追问，练习技术回答和编码题 |
| `kwai` | AI 应用经验上传助手 | 扫描本地 Agent 会话，创建 Assessment Scope，并在确认后提交评估数据 |
| `run-interview-note-defense` | 多角色、多轮面试攻防工作流 | 让面试官、候选人和记录员分别工作，围绕实习或项目经历进行追问，最后重写面试笔记 |
| `write-engineering-resume` | 工程师简历改写助手 | 把真实项目经历改写成简洁、有证据、能经得起面试追问的技术描述和简历 bullet |
| `write-interview-notes` | 中文技术面试笔记整理助手 | 创建、合并、去重和审查 Java、Agent、项目经历等 Obsidian Markdown 面试笔记 |

### `backend-interview-simulator`

包含 Java、C++、Go、AI 开发和通用后端知识库、编码题、评价标准以及面试官风格参考资料。

### `kwai`

用于操作“AI 应用经验上传助手”，包括扫描支持的本地 Agent 会话、选择评估样本、创建评估范围和提交数据。

### `run-interview-note-defense`

在正式整理面试笔记前，先进行一轮完整的攻防演练：面试官负责攻击式追问，候选人根据允许的材料回答，记录员记录过程并处理事实冲突。

### `write-engineering-resume`

强调技术事实、系统机制、边界、故障处理和可验证指标，避免把简历写成单纯的技术名词清单或模板化 STAR 描述。

### `write-interview-notes`

面向面试复习场景，生成结构化的 E/Q 编号笔记、完整的一轮回答和可选的深入追问内容，并提供 Markdown 清理、合并和校验脚本。

## 目录结构

```text
skills/
├── backend-interview-simulator/
├── kwai/
├── run-interview-note-defense/
├── write-engineering-resume/
└── write-interview-notes/
```

## 重装电脑后的恢复方式

使用 Codex 的 skill 安装脚本，从这个 GitHub 仓库一次安装全部 skill：

```powershell
python <skill-installer>/scripts/install-skill-from-github.py `
  --repo <owner>/codex-skills `
  --path skills/backend-interview-simulator `
  --path skills/kwai `
  --path skills/run-interview-note-defense `
  --path skills/write-engineering-resume `
  --path skills/write-interview-notes
```

私有仓库需要先完成 GitHub 身份验证，可以使用已有的 Git 凭据、`gh auth login`，或配置 `GITHUB_TOKEN`/`GH_TOKEN`。不要把 Token 提交到仓库中。

`.system` 中的系统 skill，以及文档、PDF、PPT、表格等插件提供的 skill，由 Codex 运行环境管理，因此没有复制到这个仓库。
