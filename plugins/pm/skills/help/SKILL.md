---
name: help
description: 使用帮助 - 查看项目管理助手所有命令
---

# 项目管理助手 - 使用帮助

## 命令格式

```
/pm:help [--lang=zh|en|ko]
```

## 执行流程

### 1. 决定语言

按以下优先级：

1. 命令参数 `--lang=zh|en|ko`（显式覆盖）
2. `.devflow/settings.local.json` 的 `language` 字段（legacy fallback: `.claude/settings.local.json`）
3. 默认 `zh`

### 2. 读取版本

```python
version = read_plugin_json("version")  # <plugin-path>/.codex-plugin/plugin.json
```

### 3. 按语言输出对应帮助内容

---

## 中文（zh，默认）

```

项目管理助手 v<version> - 使用帮助


从 PRD、需求文档和 Git 记录中提取项目数据，
按不同场景和受众生成汇报、统计、方案等内容。



**概览**
  /pm                            项目概况仪表盘

**汇报类**
  /pm:weekly [--from] [--to]     周报（本周完成/进行中/下周计划）
  /pm:monthly [--month=YYYY-MM]  月报（月度总结与统计）
  /pm:milestone <版本号>          里程碑/版本总结

**统计类**
  /pm:stats [--from] [--to]      多维度数据统计（需求/代码/贡献者）
  /pm:progress                   项目总进度（甘特视图）

**方案类**
  /pm:plan <主题>                 生成方案文档（排期/技术/资源）
  /pm:brief [--lang=zh|en]       项目简介（适合给新人或客户）

**风险类**
  /pm:risk                       风险扫描（延期/阻塞/异常检测）

**会议类**
  /pm:standup                    站会摘要（昨天/今天/阻塞）

**通用**
  /pm:ask <任何问题>              基于项目数据自由提问
  /pm:export [--format=md]       导出内容到 docs/reports/



**数据来源**
  PRD.md           产品需求文档
  active/*.md      进行中需求
  completed/*.md   已完成需求
  modules/*.md     模块文档
  git log          提交记录
  git diff         代码变更

**保存位置**
  所有输出均可选择保存到 docs/reports/ 目录



**快速开始：**
  1. /pm              查看项目概况
  2. /pm:stats        查看统计数据
  3. /pm:weekly       生成本周周报
  4. /pm:risk         扫描风险项

**前置条件：**
  - 建议先使用 /req 插件管理需求（非必须）
  - Git 仓库存在即可使用代码统计功能
  - 无需求数据时仍可使用 stats/ask 命令


```

---

## English (en)

```

Project Management Assistant v<version> — Help


Extracts project data from PRD, requirement docs, and Git
history to generate reports, stats, and plans for different
audiences.



**Overview**
  /pm                            Project dashboard

**Reports**
  /pm:weekly [--from] [--to]     Weekly report (done/in-progress/next week)
  /pm:monthly [--month=YYYY-MM]  Monthly report (summary + stats)
  /pm:milestone <version>        Milestone / release summary

**Stats**
  /pm:stats [--from] [--to]      Multi-dimensional stats (reqs/code/contributors)
  /pm:progress                   Project progress (Gantt view)

**Plans**
  /pm:plan <topic>               Plan doc (schedule / technical / resource)
  /pm:brief [--lang=zh|en]       Project brief (for onboarding / clients)

**Risks**
  /pm:risk                       Risk scan (delays / blockers / anomalies)

**Meetings**
  /pm:standup                    Standup summary (yesterday / today / blockers)

**General**
  /pm:ask <any question>         Free-form Q&A over project data
  /pm:export [--format=md]       Export output to docs/reports/



**Data sources**
  PRD.md           Product requirement doc
  active/*.md      Active requirements
  completed/*.md   Completed requirements
  modules/*.md     Module docs
  git log          Commit history
  git diff         Code changes

**Persistence**
  Every output can optionally be saved to docs/reports/



**Quick start:**
  1. /pm              View project dashboard
  2. /pm:stats        View stats
  3. /pm:weekly       Generate this week's report
  4. /pm:risk         Scan for risks

**Prerequisites:**
  - Recommended: manage requirements via the /req plugin (optional)
  - A Git repository is enough for code statistics
  - stats/ask work even without requirement data


```

---

## 한국어 (ko)

```

프로젝트 관리 도우미 v<version> - 도움말


PRD, 요구사항 문서, Git 기록에서 프로젝트 데이터를 추출하여
다양한 대상자에 맞춘 리포트, 통계, 기획안을 생성합니다.



**개요**
  /pm                            프로젝트 대시보드

**리포트**
  /pm:weekly [--from] [--to]     주간 리포트 (완료/진행 중/다음 주 계획)
  /pm:monthly [--month=YYYY-MM]  월간 리포트 (요약 + 통계)
  /pm:milestone <버전>            마일스톤/릴리즈 요약

**통계**
  /pm:stats [--from] [--to]      다차원 통계 (요구사항/코드/기여자)
  /pm:progress                   프로젝트 진척도 (간트 뷰)

**기획안**
  /pm:plan <주제>                 기획안 문서 (일정/기술/리소스)
  /pm:brief [--lang=zh|en]       프로젝트 브리프 (온보딩/고객용)

**리스크**
  /pm:risk                       리스크 스캔 (지연/블로커/이상)

**미팅**
  /pm:standup                    스탠드업 요약 (어제/오늘/블로커)

**공통**
  /pm:ask <질문>                  프로젝트 데이터 기반 자유 질의응답
  /pm:export [--format=md]       docs/reports/ 에 내보내기



**데이터 소스**
  PRD.md           제품 요구사항 문서
  active/*.md      진행 중 요구사항
  completed/*.md   완료된 요구사항
  modules/*.md     모듈 문서
  git log          커밋 기록
  git diff         코드 변경

**저장 위치**
  모든 출력은 docs/reports/ 에 선택적으로 저장 가능



**빠른 시작:**
  1. /pm              프로젝트 대시보드 조회
  2. /pm:stats        통계 조회
  3. /pm:weekly       이번 주 리포트 생성
  4. /pm:risk         리스크 스캔

**전제 조건:**
  - /req 플러그인으로 요구사항 관리 권장 (필수 아님)
  - Git 레포가 있으면 코드 통계 사용 가능
  - 요구사항 데이터가 없어도 stats/ask 사용 가능


```

---

## 持久化语言偏好

在 `.devflow/settings.local.json` 中设置一次：

```json
{
  "language": "en"
}
```

后续 `/req:help`、`/api:help`、`/pm:help` 都会默认用该语言。

## 用户输入

$ARGUMENTS
