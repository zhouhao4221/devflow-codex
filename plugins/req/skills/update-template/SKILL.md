---
name: update-template
description: |
  更新模板 - 将插件最新模板同步到项目本地
---

# 更新模板文件

将插件 `templates/` 目录下的最新模板同步到项目本地 `docs/requirements/`，覆盖旧版本。

> 存储路径规则见 [_storage.md](./_storage.md)

## 命令格式

```
/req:update-template [模板名称] [--force]
```

**示例：**
- `/req:update-template` - 交互选择要更新的模板
- `/req:update-template requirement` - 更新需求模板
- `/req:update-template all` - 更新所有模板
- `/req:update-template requirement --force` - 强制覆盖，跳过对比确认

---

## 可更新的模板

| 模板名称 | 插件源文件（相对插件根目录） | 项目目标文件 |
|---------|--------------------------|------------|
| `requirement` | `templates/requirement-template.md` | `docs/requirements/templates/requirement-template.md` |
| `quick` | `templates/quick-template.md` | `docs/requirements/templates/quick-template.md` |
| `module` | `templates/module-template.md` | `docs/requirements/templates/module-template.md` |
| `prd` | `templates/prd-template.md` | `docs/requirements/templates/prd-template.md` |
| `release-prompt` | `templates/release-prompt-template.md` | `docs/prompt/release.md` |
| `all` | 以上全部 | 以上全部 |

---

## 执行流程

### 1. 定位插件根目录

本命令文件位于插件的 `commands/` 目录下。通过本文件自身路径向上一级即可得到插件根目录：

```
本文件路径: <插件根目录>/commands/update-template.md
插件根目录: 本文件所在目录的父目录
模板目录:   <插件根目录>/templates/
```

**定位方式**：读取 `.claude/settings.local.json` 中的 `extraKnownMarketplaces` 配置，或通过当前项目的 `.claude/settings.local.json` 找到插件注册信息。如果找不到，使用以下回退策略：

```
1. 读取 ~/.claude/settings.json 的 extraKnownMarketplaces 字段
2. 找到 name 包含 "req" 的插件条目
3. 提取 source.path 作为插件根目录
4. 若以上均失败，提示用户手动指定插件路径
```

**重要**：必须先确认插件根目录存在 `templates/` 子目录，且目标模板文件存在，再继续后续步骤。

### 2. 前置检查

```bash
# 检查本地存储目录是否存在
LOCAL_ROOT=docs/requirements
if [ ! -d "$LOCAL_ROOT" ]; then
    echo "本地需求目录不存在，请先执行 /req:init <project-name>"
    exit 1
fi

# 检查仓库角色
ROLE=$(cat .claude/settings.local.json 2>/dev/null | jq -r '.requirementRole // "primary"')
if [ "$ROLE" = "readonly" ]; then
    echo "只读仓库不支持更新模板"
    exit 1
fi
```

### 3. 选择模板

如果未指定模板名称，交互选择：

```
请选择要更新的模板：

1. requirement - 需求模板 (requirement-template.md)
2. quick       - 快速修复模板 (quick-template.md)
3. module      - 模块模板 (module-template.md)
4. prd         - PRD 模板 (prd-template.md)
a. all         - 更新全部模板

请输入编号或名称:
```

### 4. 读取插件模板并对比

对每个待更新的模板：

1. **读取插件源模板**：使用 Read 工具读取 `<插件根目录>/templates/<模板文件>`
2. **读取项目本地模板**：使用 Read 工具读取 `docs/requirements/<目标文件>`（如存在）
3. **对比内容**

**情况 A：本地文件不存在**
```
模板 requirement:
  插件版本: <插件根目录>/templates/requirement-template.md
  本地文件: 不存在（将新建）
```

**情况 B：内容相同**
```
模板 requirement: 已是最新，无需更新
```

**情况 C：内容不同**

展示主要差异摘要（不展示完整 diff，而是结构化对比）：

```
模板 requirement:
  插件版本: <插件根目录>/templates/requirement-template.md
  本地文件: docs/requirements/templates/requirement-template.md

差异摘要:
  - 插件版本新增章节: "十三、非功能需求"
  - 插件版本修改章节: "五、接口需求"（表格结构调整）
  - 本地独有内容: "五、数据模型" 中有自定义字段

更新将覆盖本地文件，本地自定义内容将丢失
```

**--force 模式**：跳过对比确认，直接覆盖。

### 5. 执行更新

使用 Write 工具将插件模板内容写入项目本地文件：

| 模板名称 | 读取（Read） | 写入（Write） |
|---------|-------------|-------------|
| `requirement` | `<插件根目录>/templates/requirement-template.md` | `docs/requirements/templates/requirement-template.md` |
| `quick` | `<插件根目录>/templates/quick-template.md` | `docs/requirements/templates/quick-template.md` |
| `module` | `<插件根目录>/templates/module-template.md` | `docs/requirements/templates/module-template.md` |
| `prd` | `<插件根目录>/templates/prd-template.md` | `docs/requirements/templates/prd-template.md` |

**注意**：PRD 模板更新时保留原始模板变量（`{{PROJECT_NAME}}`、`{{DATE}}`），不做变量替换。已有的 `PRD.md` 是项目文档，不会被覆盖。PRD 模板更新到 `prd-template.md`，仅影响后续新建项目时使用。

### 6. 同步到全局缓存

更新后自动同步模板到全局缓存：

```bash
PROJECT=$(cat .claude/settings.local.json 2>/dev/null | jq -r '.requirementProject // empty')
if [ -n "$PROJECT" ]; then
    CACHE_ROOT=~/.claude-requirements/projects/$PROJECT
    mkdir -p $CACHE_ROOT/templates
    cp $LOCAL_ROOT/templates/*.md $CACHE_ROOT/templates/ 2>/dev/null
fi
```

### 7. 输出结果

**单个模板更新：**
```
已更新模板: requirement
  源文件: <插件根目录>/templates/requirement-template.md
  目标: docs/requirements/templates/requirement-template.md
  缓存同步: 已完成

新创建的需求将使用更新后的模板。已有需求文档不受影响。
```

**批量更新（all）：**
```
模板更新结果:

  requirement  已更新
  quick        已更新
  module       已是最新
  prd          已更新

共更新 3 个模板，1 个无需更新。
新创建的需求将使用更新后的模板。已有需求文档不受影响。
```

---

## 错误处理

| 错误场景 | 处理方式 |
|---------|---------|
| 插件根目录无法定位 | 提示：无法定位插件目录，请检查 `~/.claude/settings.json` 中的 `extraKnownMarketplaces` 配置 |
| 插件 templates/ 目录不存在 | 提示：插件模板目录不存在，插件安装可能不完整 |
| 本地需求目录不存在 | 提示先执行 `/req:init` |
| 只读仓库 | 提示只读仓库不支持更新模板 |
| 用户取消 | 提示已取消，不做任何修改 |

---

## 用户输入

$ARGUMENTS
