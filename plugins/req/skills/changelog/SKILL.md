---
name: changelog
description: 生成版本说明 - 基于 Git 记录生成 Changelog
---

# 生成版本说明

根据 Git 提交记录和已完成需求，生成版本升级说明文档。

> 此命令**不受仓库角色限制**，readonly 仓库也可执行。
> 生成的文件保存在 `docs/changelogs/` 目录，不触发缓存同步。

## 命令格式

```
/req:changelog <version> [--from=<tag|commit>] [--to=<tag|commit>]
```

**参数说明：**
- `<version>`：**必填**，版本号（如 `v1.2.0`、`1.2.0`）
- `--from`：可选，起始点（tag 或 commit hash），默认为上一个 git tag
- `--to`：可选，结束点（tag 或 commit hash），默认为 HEAD

**示例：**
- `/req:changelog v1.2.0` — 从上一个 tag 到 HEAD
- `/req:changelog v1.2.0 --from=v1.1.0` — 从 v1.1.0 到 HEAD
- `/req:changelog v1.2.0 --from=v1.1.0 --to=v1.2.0` — 指定完整范围
- `/req:changelog v1.2.0 --from=abc1234` — 从某个 commit 开始

---

## 执行流程

### 1. 参数校验

`version` 必填，缺失时打印用法后退出。

### 2. 确定 Git 范围

> **被 `/req:release` 调用时**：`/req:release` 会显式传入 `--from`，跳过下面的自动检测链，draft 模式对本步无影响。
> **用户手动调用时**：走下方 draft-aware 回退链。

`TO_REF` 默认 HEAD。`FROM_REF` 按以下优先级解析（v3.0.0+ 新增 draft 感知）：

1. `--from` 参数显式指定 → 直接使用
2. 查询平台最近一个 Release（含 draft）的 target SHA → 仅当 `repoType` 为 gitea / github 且 API 可达时；打印所用 Release 名称
3. `git describe` 取最近一个本地 git tag；若同时存在未 publish 的 draft release，打印 ⚠️ 提示（changelog 范围可能与预期不一致，建议显式传 `--from=<draft-target-sha>`）
4. 仓库首次 commit → 无任何 tag 时的兜底，打印 ⚠️ 警告

**为什么要 draft 感知**：v3.0.0 起 `/req:release` 默认 draft，不再本地打 tag。如果用户先跑 `/req:release v1.2.0`（draft 未 publish）→ 后跑 `/req:changelog v1.3.0`，原来的 `git describe` 会返回更早的 tag（比如 `v1.1.0`），导致 v1.3.0 的 changelog 多包含了一整个版本的 commits。新回退链优先读平台 Release（含 draft）的 SHA，或在走 git tag 回退时警告用户。

**repoType=other 的行为**：仍走原有 `git describe` 链，无 draft 感知（`other` 类型无 API 可查）。

### 3. 读取 Git 提交记录

从 `FROM_REF..TO_REF` 范围内（不含 merge commit）提取：短 hash、提交日期、提交消息。

### 4. 按提交前缀分类

将提交按前缀分类（中文优先，兼容英文）：

| 中文前缀 | 英文前缀 | 分类 |
|---------|---------|------|
| `新功能` | `feat` | 新功能 (Features) |
| `修复` | `fix` | 问题修复 (Bug Fixes) |
| `重构` | `refactor` | 重构优化 (Refactoring) |
| `优化` | `perf` | 性能优化 (Performance) |
| `文档` | `docs` | 文档更新 (Documentation) |
| `测试` | `test` | 测试 (Tests) |
| `构建`/`样式` | `chore`/`ci`/`build`/`style` | 其他变更 (Others) |
| 无前缀/不识别 | 无前缀/不识别 | 其他变更 (Others) |

**分类规则：**
- 按 `前缀: 描述` 格式解析（中文或英文前缀均可）
- 无法识别前缀的统一归入「其他变更」
- 空分类不输出对应章节

### 5. 关联已完成需求

按 `requirementRole` 确定需求目录（readonly → 主仓需求目录；primary → 本地，不存在时回退缓存）。从 commit messages 中提取 `REQ-XXX` / `QUICK-XXX` 编号，读取对应需求文档的标题和类型。同时扫描 active/ 目录（需求可能尚未完成但已有 commit）。

### 6. 检查目标文件

目标路径固定为 `docs/changelogs/<version>.md`，目录不存在时自动创建。文件已存在时询问用户是否覆盖。

### 7. 生成版本说明文档

使用 Write 工具生成 `$OUTPUT_DIR/<version>.md`，格式如下：

```markdown
# <version> 版本说明

> 发布日期：YYYY-MM-DD
> 版本范围：<from-ref>..<to-ref>
> 提交数量：N

## 关联需求

| 编号 | 标题 | 类型 |
|------|------|------|
| REQ-XXX | 需求标题 | 后端 |
| QUICK-XXX | 快速修复标题 | 全栈 |

## 新功能 (Features)

- 描述 (`hash`)

## 问题修复 (Bug Fixes)

- 描述 (`hash`)

## 重构优化 (Refactoring)

- 描述 (`hash`)

## 性能优化 (Performance)

- 描述 (`hash`)

## 其他变更

- 描述 (`hash`)

---
*由 /req:changelog 自动生成*
```

**格式规则：**
- 没有匹配提交的分类章节**不输出**（不保留空章节）
- 没有关联需求时**不输出**「关联需求」章节
- 每条提交包含简短 hash 方便回溯
- 提交按时间倒序排列（最新在前）

### 8. 输出生成报告

```
✅ 版本说明已生成！


Changelog：<version>


版本信息
版本号：<version>
发布日期：YYYY-MM-DD
版本范围：<from-ref>..<to-ref>
提交数量：N

变更统计
新功能：X
问题修复：X
重构优化：X
性能优化：X
其他变更：X

关联需求：X 个
REQ-001 需求标题
QUICK-003 快速修复标题

文件位置
$OUTPUT_DIR/<version>.md



后续操作：
- 查看文件：cat $OUTPUT_DIR/<version>.md
- 重新生成：/req:changelog <version> --from=<tag>
- 创建 git tag：git tag <version>
```

---

## 边界情况处理

| 场景 | 处理方式 |
|------|---------|
| 没有 git tag | 从仓库首次提交开始，显示警告 |
| 范围内无提交 | 终止操作，提示范围无效 |
| 文件已存在 | 询问用户是否覆盖 |
| 无关联需求 | 省略「关联需求」章节 |
| commit 不遵循 conventional commits | 归入「其他变更」 |
| changelog 目录不存在 | 自动创建 `docs/changelogs/` |

## 用户输入

$ARGUMENTS
