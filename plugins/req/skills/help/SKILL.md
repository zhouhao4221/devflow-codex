---
name: help
description: |
  使用教程 - 查看插件完整使用指南
---

# 使用教程

读取并展示插件使用教程，支持中文 / 英文 / 韩文三语。

## 执行流程

### 1. 决定语言

按以下优先级决定语言：

1. 命令参数 `--lang=zh|en|ko`（显式覆盖）
2. `.claude/settings.local.json` 的 `language` 字段
3. 默认 `zh`

### 2. 读取教程文件

按语言选择教程文件：

| lang | 文件路径 |
|------|---------|
| `zh`（默认） | `docs/tutorial.md` |
| `en` | `docs/tutorial.en.md` |
| `ko` | `docs/tutorial.ko.md` |

> 插件安装路径下无此文件时，回退到项目仓库根的 `docs/tutorial.<lang>.md`。

### 3. 决定输出范围

- 无章节参数 → 输出章节索引
- 有章节参数 → 按章节名或编号模糊匹配，仅输出对应章节

## 章节索引

无参数时展示对应语言的章节索引。

### 中文（zh）

```
需求工作流插件 - 使用教程

章节：
 1. 安装与初始化（含架构描述、分支策略、Gitea Token 配置、reinit、缓存重建）
 2. 创建需求
 3. 评审流程
 4. 开发阶段（含分支管理、PR 创建）
 5. 测试阶段
 6. 完成归档
 7. 查看与管理
 8. 模块管理
 9. PRD 管理
10. 版本管理
11. 跨仓库协作
12. 完整流程图

输入章节编号查看详情，或直接阅读完整教程。
```

### English (en)

```
Requirements Workflow Plugin — Tutorial

Sections:
 1. Installation & initialization (architecture, branch strategy, Gitea token, reinit, cache rebuild)
 2. Creating requirements
 3. Review flow
 4. Development (branch management, PR creation)
 5. Testing
 6. Archival
 7. Browsing & management
 8. Module management
 9. PRD management
10. Versioning
11. Cross-repo collaboration
12. Full flow diagram

Enter a section number to view details, or read the full tutorial.
```

### 한국어 (ko)

```
요구사항 워크플로우 플러그인 - 튜토리얼

섹션:
 1. 설치 & 초기화 (아키텍처, 브랜치 전략, Gitea Token, 재초기화, 캐시 재구축)
 2. 요구사항 생성
 3. 리뷰 플로우
 4. 개발 단계 (브랜치 관리, PR 생성)
 5. 테스트 단계
 6. 완료 및 아카이브
 7. 조회 & 관리
 8. 모듈 관리
 9. PRD 관리
10. 버전 관리
11. 크로스 레포 협업
12. 전체 플로우 다이어그램

섹션 번호를 입력하여 상세 조회, 또는 전체 튜토리얼 읽기.
```

## 命令格式

```
/req:help [章节名或编号] [--lang=zh|en|ko]
```

示例：
- `/req:help` → 中文章节索引（或 settings.local.json 中设定的语言）
- `/req:help --lang=en` → English section index
- `/req:help --lang=ko` → 한국어 섹션 인덱스
- `/req:help 4` → 第四章「开发阶段」
- `/req:help 4 --lang=en` → Section 4 "Development"
- `/req:help branch --lang=en` → English match on "branch management"

## 持久化语言偏好（可选）

如果想省去每次加 `--lang` 参数，在 `.claude/settings.local.json` 中设置：

```json
{
  "language": "en"
}
```

后续所有 `/req:help`、`/api:help`、`/pm:help` 都会默认用该语言。

## 用户输入

$ARGUMENTS
