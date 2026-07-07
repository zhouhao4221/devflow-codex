---
name: update
description: 热更新插件 - 拉取最新命令文件和技能，所有项目立即生效
---

# 热更新 req 插件

拉取最新版本，所有使用该插件的项目立即生效（无需重装）。

`--check`：只检查是否有更新，不执行拉取。

## 执行流程

### 1. 定位插件目录

**优先级**：本地目录源 > Claude 缓存克隆目录

```bash
# 1a. 查找 directory 类型源（本地开发安装）
SOURCE_PATH=$(jq -r '
  .extraKnownMarketplaces | to_entries[] |
  select(.value.source.source == "directory") |
  .value.source.path
' ~/.claude/settings.json .claude/settings.local.json 2>/dev/null | head -1)

# 1b. 查找 Claude 缓存的克隆目录（GitHub/远程源安装）
if [ -z "$SOURCE_PATH" ]; then
    # Claude Code 将远程 marketplace 克隆到 ~/.claude/plugins/marketplaces/<name>/
    # 从 settings 取 marketplace 名称，映射到缓存目录
    MARKETPLACE_NAME=$(jq -r '
      .extraKnownMarketplaces | to_entries[] |
      select(.value.source.source != "directory") |
      .key
    ' ~/.claude/settings.json .claude/settings.local.json 2>/dev/null | head -1)

    if [ -n "$MARKETPLACE_NAME" ]; then
        CACHE_PATH="$HOME/.claude/plugins/marketplaces/$MARKETPLACE_NAME"
        if [ -d "$CACHE_PATH/.git" ]; then
            SOURCE_PATH="$CACHE_PATH"
        fi
    fi
fi
```

找不到时输出：
```
❌ 无法定位插件目录。
   请检查 ~/.claude/settings.json 中的 extraKnownMarketplaces 配置。
```

退出。

### 2. 检查远程更新

```bash
git -C "$SOURCE_PATH" fetch origin --quiet

LOCAL=$(git -C "$SOURCE_PATH" rev-parse HEAD)
REMOTE=$(git -C "$SOURCE_PATH" rev-parse "@{u}" 2>/dev/null)
CURRENT_VER=$(jq -r '.version // "unknown"' "$SOURCE_PATH/plugins/req/.claude-plugin/plugin.json" 2>/dev/null)
```

已是最新时：
```
✅ 已是最新版本（v<CURRENT_VER>）
   源目录：<SOURCE_PATH>
```

有更新时打印待拉取的提交列表：
```
发现更新（当前 v<CURRENT_VER>）：
  <git log HEAD..@{u} --oneline --no-merges 的输出>
```

**`--check` 模式**：到此退出，不执行拉取。

### 3. 执行拉取

```bash
git -C "$SOURCE_PATH" pull --ff-only origin
NEW_VER=$(jq -r '.version // "unknown"' "$SOURCE_PATH/plugins/req/.claude-plugin/plugin.json" 2>/dev/null)
```

成功：
```
✅ 插件已更新至 v<NEW_VER>
   源目录：<SOURCE_PATH>
   所有使用此插件的项目立即生效，无需重启。
```

失败（本地有分歧提交）：
```
❌ 拉取失败：源目录存在本地修改或分歧提交。
   请手动处理：cd <SOURCE_PATH> && git status
```

### 4. 检查项目 prompt 文件

**触发条件**：当前目录存在 `docs/prompt/`（说明项目已创建架构文档）。`--check` 模式同样执行此步骤。

读取 `$SOURCE_PATH/plugins/req/schemas/prompt-schema.md`，对 schema 中每个文件逐项检查：

1. 文件是否存在
2. 文件存在时，必需关键词是否在标题或正文中出现

按结果分级输出：

```
Prompt 文件检查（schema v<VERSION>）：

  docs/prompt/architecture.md
    ✅ 技术栈      ✅ 分层      ✅ 目录      ❌ 命名规范（必需，/req:dev 依赖）
    ⚠️  错误处理（推荐，/req:dev 可能生成不一致的错误返回）

  docs/prompt/testing.md
    ⚠️  文件不存在（可选，/req:test 将使用内置默认值）

建议：补充 1 个必需章节，详见 plugins/req/schemas/prompt-schema.md
```

全部覆盖时：
```
✅ Prompt 文件结构完整
```

`docs/prompt/` 不存在时跳过，不输出任何内容（项目尚未初始化架构文档，属正常状态）。

## 用户输入

$ARGUMENTS
