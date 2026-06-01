# DevFlow Skills

DevFlow 技能包 —— 80 个 AI 技能指令，一键安装到 7 种 AI 工具。

## 快速开始

```bash
# 安装全部技能
npx @zhouhao4221/devflow-skills install --tool opencode --all

# 安装指定插件
npx @zhouhao4221/devflow-skills install --tool cursor --plugin req

# 安装单个技能
npx @zhouhao4221/devflow-skills install --tool claude --skill req-dev

# 查看所有技能
npx @zhouhao4221/devflow-skills list
```

首次运行 `npx` 即用，无需安装任何依赖。

## 支持的工具

| 工具 | --tool 值 | 安装路径 |
|------|-----------|----------|
| Claude Code | `claude` | `plugins/<plugin>/skills/<name>/` |
| OpenCode | `opencode` | `.agents/skills/<plugin>-<name>/` |
| Codex | `codex` | `.agents/skills/<plugin>-<name>/` |
| Cursor | `cursor` | `.agents/skills/<plugin>-<name>/` |
| GitHub Copilot | `copilot` | `.agents/skills/<plugin>-<name>/` |
| CodeBuddy | `codebuddy` | `.agents/skills/<plugin>-<name>/` |
| Windsurf | `windsurf` | `.agents/skills/<plugin>-<name>/` |

Claude Code 使用分层目录保留插件作用域；其余工具采用 `插件-名称` 扁平命名，保证全局唯一。

## 命令参考

### install — 安装技能

```bash
npx @zhouhao4221/devflow-skills install --tool <工具名> [--all | --plugin <插件> | --skill <名>] [--dir <路径>] [-g] [--symlink]
```

| 参数 | 说明 |
|------|------|
| `--tool` | 目标 AI 工具（必填） |
| `--all` | 安装全部 80 个技能 |
| `--plugin` | 按插件安装（`req` / `api` / `pm` / `diag` / `uat`） |
| `--skill` | 安装指定技能，可重复使用 |
| `--dir` | 目标项目目录，默认当前目录 |
| `-g`, `--global` | 安装到全局目录（`~/` 下） |
| `--symlink` | 符号链接模式，多工具共享同一份文件 |

### list — 列出技能

```bash
npx @zhouhao4221/devflow-skills list [--plugin <插件>] [--filter <关键词>] [--format json]
```

### uninstall — 卸载技能

```bash
npx @zhouhao4221/devflow-skills uninstall --tool <工具名> [--all | --skill <名>] [--dir <路径>] [-g]
```

### add — 从 GitHub 仓库安装

```bash
npx @zhouhao4221/devflow-skills add <owner/repo> --list              # 浏览仓库中的技能
npx @zhouhao4221/devflow-skills add <owner/repo> --tool cursor --all  # 安装全部
```

## 技能分类

| 插件 | 数量 | 用途 |
|------|------|------|
| `req` | 46 | 需求全生命周期：创建、评审、开发、测试、发布 |
| `api` | 8 | Swagger/OpenAPI 解析、字段映射、代码生成 |
| `pm` | 14 | 项目管理：周报、站会、风险跟踪、里程碑 |
| `diag` | 5 | 生产诊断：日志审计、堆栈分析 |
| `uat` | 7 | UI 验收测试：用例执行、Bug 上报、报告生成 |

## 与 devflow-claude 的关系

本仓库的技能源自 [devflow-claude](https://github.com/zhouhao4221/devflow-claude)（Claude Code 专属插件），独立出来作为跨工具的技能分发中心。devflow-claude 通过 `scripts/setup-claude.sh` 同步本仓库的技能文件，保持两边一致。

## 手动安装（适配器脚本）

如果不想用 CLI，也可以通过脚本直接生成：

```bash
# Claude Code（分层目录）
./scripts/setup-claude.sh . ../devflow-claude

# OpenCode / Codex / Cursor 等（扁平目录）
./scripts/setup-opencode.sh . ~/.agents/skills
./scripts/setup-codex.sh . ~/.agents/skills --gen-openai-yaml
```

## 校验

```bash
./scripts/validate-skills.sh --ci
```

检查项：SKILL.md frontmatter 完整性、name 字段合规、skill-bindings.json 交叉引用一致性。

## 许可证

[Apache License 2.0](LICENSE)
