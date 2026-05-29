---
name: changelog-generator
description: |
  版本说明生成助手。仅在执行 /req:changelog 命令时触发。
  根据 Git 提交记录自动分类并生成结构化的版本升级说明。
---

# 版本说明生成助手

根据 Git 提交记录生成结构化的版本升级说明（Changelog）。

## 触发条件

仅在执行 `/req:changelog` 命令时触发。

## 工作流程

### 1. 收集 Git 提交

使用 Bash 工具执行 git 命令，获取指定范围内的提交记录：

```bash
# 获取提交列表（不含 merge commits）
git log <from>..<to> --pretty=format:"%h|%ai|%s" --no-merges

# 获取变更文件统计
git diff --stat <from>..<to>
```

### 2. 解析提交前缀

按 `前缀: 描述` 格式解析每条提交消息，同时兼容英文 Conventional Commits 格式：

```
输入：新功能: 实现部门渠道关联 (REQ-001)
解析：type=新功能, message=实现部门渠道关联, req=REQ-001

输入：feat: add user login
解析：type=feat→新功能, message=add user login
```

**分类映射（中文优先，兼容英文）：**

| 中文前缀 | 英文前缀 | 章节标题 | 优先级 |
|---------|---------|---------|--------|
| `新功能` | `feat` | 新功能 (Features) | 1 |
| `修复` | `fix` | 问题修复 (Bug Fixes) | 2 |
| `重构` | `refactor` | 重构优化 (Refactoring) | 3 |
| `优化` | `perf` | 性能优化 (Performance) | 4 |
| `文档` | `docs` | 文档更新 (Documentation) | 5 |
| `测试` | `test` | 测试 (Tests) | 6 |
| `构建`/`样式` | `chore`/`ci`/`build`/`style` | 其他变更 (Others) | 7 |
| 无前缀/不识别 | 无前缀/不识别 | 其他变更 (Others) | 7 |

### 3. 提取关联需求编号

从 commit messages 中提取需求编号：

- 正则：`(REQ-\d+|QUICK-\d+)`
- 去重后查找对应需求文档
- 读取需求标题和类型字段

### 4. 生成 Changelog 内容

**输出格式：**

```markdown
# <version> 版本说明

> 发布日期：YYYY-MM-DD
> 版本范围：<from>..<to>
> 提交数量：N

## 关联需求

| 编号 | 标题 | 类型 |
|------|------|------|
| REQ-XXX | 需求标题 | 后端 |

## 新功能 (Features)

- 描述 (`hash`)
- 描述 (`hash`)

## 问题修复 (Bug Fixes)

- 描述 (`hash`)

---
*由 /req:changelog 自动生成*
```

### 5. 格式规则

1. **空分类不输出**：没有匹配提交的分类章节直接省略
2. **无关联需求不输出**：没有 REQ/QUICK 引用时省略「关联需求」章节
3. **提交倒序排列**：最新的提交在前
4. **去除前缀**：输出时去掉 `新功能:` 等前缀，仅保留描述内容
5. **hash 用反引号包裹**：方便区分和查找

## 内容优化原则

1. **保留原始 commit message**：不修改、不美化提交描述
2. **去除重复**：同一 scope 下相似描述只保留一条（如 merge 导致的重复）
3. **Breaking Changes 高亮**：如果 commit 包含 `BREAKING CHANGE` 或 `!`，在对应条目前加 **⚠️ BREAKING**
4. **Co-authored 提交**：保留主提交消息，忽略 co-author 信息
