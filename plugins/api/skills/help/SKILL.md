---
name: help
description: 使用教程 - 查看 API 对接插件完整使用指南
---

# API 对接插件 - 使用教程

展示 API 对接插件的使用指南，支持中文 / 英文 / 韩文三语。

## 执行流程

### 1. 决定语言

按以下优先级：

1. 命令参数 `--lang=zh|en|ko`（显式覆盖）
2. `.devflow/settings.local.json` 的 `language` 字段（legacy fallback: `.claude/settings.local.json`）
3. 默认 `zh`

### 2. 读取教程文件

按语言选择教程文件（相对于插件目录）：

| lang | 文件路径 |
|------|---------|
| `zh`（默认） | `<plugin-path>/docs/tutorial.zh.md` |
| `en` | `<plugin-path>/docs/tutorial.en.md` |
| `ko` | `<plugin-path>/docs/tutorial.ko.md` |

### 3. 决定输出范围

- 无章节参数 → 输出章节索引
- 有章节参数 → 按章节名或编号模糊匹配，仅输出对应章节

## 章节索引

无参数时展示对应语言的章节索引。

### 中文（zh）

```
API 对接插件 - 使用教程

章节：
 1. 快速开始
 2. 配置管理
 3. 导入 Swagger
 4. 搜索接口
 5. 字段映射
 6. 代码生成
 7. 自动检测
 8. 常见问题

输入章节编号查看详情。
```

### English (en)

```
API Plugin — Tutorial

Sections:
 1. Quick start
 2. Configuration
 3. Import Swagger
 4. Search endpoints
 5. Field mapping
 6. Code generation
 7. Auto-detection
 8. FAQ

Enter a section number to view details.
```

### 한국어 (ko)

```
API 플러그인 - 튜토리얼

섹션:
 1. 빠른 시작
 2. 설정 관리
 3. Swagger 임포트
 4. 엔드포인트 검색
 5. 필드 매핑
 6. 코드 생성
 7. 자동 감지
 8. FAQ

섹션 번호를 입력하여 상세 조회.
```

## 命令格式

```
/api:help [章节名或编号] [--lang=zh|en|ko]
```

示例：
- `/api:help` → 中文章节索引（或 `.devflow/settings.local.json` 中设定的语言）
- `/api:help --lang=en` → English section index
- `/api:help 5` → 第 5 章「字段映射」
- `/api:help 5 --lang=ko` → 섹션 5 "필드 매핑"
- `/api:help search --lang=en` → English match on "Search endpoints"

## 持久化语言偏好

在 `.devflow/settings.local.json` 中设置：

```json
{
  "language": "en"
}
```

后续 `/req:help`、`/api:help`、`/pm:help` 都会默认用该语言。

## 用户输入

$ARGUMENTS
