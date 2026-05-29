---
name: specs
description: |
  规范文档管理 - 项目级公共知识层，集中沉淀散落在代码中的枚举、规则、契约
---

# 规范文档管理

项目级公共知识层——把散落在代码各处、不易直接阅读的枚举值、业务规则、接口契约整理成可查阅的文档，供 AI 和人随时参考。

**典型内容**：订单状态枚举含义、错误码定义、跨模块共用的业务规则、前后端字段命名约定。

## 命令格式

```
/req:specs [子命令] [文档名]
```

## 子命令

| 子命令 | 说明 | 权限 | 示例 |
|--------|------|------|------|
| (空) | 列出所有规范文档 | 所有角色 | `/req:specs` |
| `new` | 创建规范文档 | 仅 primary | `/req:specs new 订单数据类型` |
| `show` | 查看规范文档 | 所有角色 | `/req:specs show order-types` |
| `edit` | 编辑规范文档 | 仅 primary | `/req:specs edit order-types` |

---

## 存储路径

```
<需求根目录>/specs/        # 本地（primary）
~/.claude-requirements/projects/<project>/specs/   # 缓存（readonly 读此处）
```

- **primary**：读写本地 `docs/requirements/specs/`
- **readonly**：只读缓存，禁止写操作

---

## 规范文档格式

每份文档 frontmatter 必须包含：

```markdown
---
category: <分类>
description: <一句话描述>
updated: <YYYY-MM-DD>
---
```

**常见分类**：数据类型、接口契约、错误码、业务规则、编码规范、配置说明

正文格式不作统一要求，同一分类下的文档应保持风格一致，建议按分类采用如下风格：

| 分类 | 建议风格 |
|------|---------|
| 数据类型 / 枚举 | 表格（值、含义、备注） |
| 错误码 | 表格（code、message、适用场景） |
| 接口契约 | 表格（字段、类型、说明）+ 示例 |
| 业务规则 | 编号列表（规则 + 适用条件） |
| 编码规范 | 列表 |

列表展示时从 frontmatter 提取 `category`、`description`、`updated` 三个字段。

---

## 约束

- **文件命名**：用户输入中文名时，生成 kebab-case 英文文件名（如 `订单数据类型` → `order-types.md`）
- **查找**：`show` / `edit` 支持中文名或文件名模糊匹配
- **edit**：修改完成后必须更新 `updated` 字段为当天日期
- **缓存同步**：Write/Edit 操作 `specs/` 下的文件后，PostToolUse Hook 自动同步到缓存（仅 primary）

---

## 列表输出格式

```
规范文档

| 文档 | 分类 | 描述 | 更新时间 |
|------|------|------|----------|
| order-types | 数据类型 | 订单相关枚举和结构体定义 | 2026-03-25 |

共 N 份规范文档

/req:specs show <名称> · /req:specs new <名称> · /req:specs edit <名称>
```

无文档时提示：`/req:specs new <名称>`

---

## 用户输入

$ARGUMENTS
