---
name: stats
description: 项目数据统计 - 需求、代码、贡献者等多维度统计分析
---

# 项目数据统计

> **Audience:** Product Manager

生成项目多维度统计数据，包括需求进度、代码活动、贡献者分布等。

## 命令格式

```
/pm:stats [--from=YYYY-MM-DD] [--to=YYYY-MM-DD] [--save]
```

**参数说明：**
- `--from`：可选，统计起始日期，默认项目首次提交
- `--to`：可选，统计截止日期，默认今天
- `--save`：可选，直接保存不询问

**示例：**
- `/pm:stats` — 全量统计
- `/pm:stats --from=2026-03-01` — 本月统计
- `/pm:stats --from=2026-03-01 --to=2026-03-26` — 指定范围

---

## 执行流程

### 1. 解析参数和路径

```python
from_date, to_date = parse_date_range(args.from, args.to, default_range="all")
# 解析需求数据路径（参考 _common.md）
```

### 2. 采集数据

#### 2.1 需求数据

读取所有需求文档，统计：总数、进行中/已完成分布、按状态/类型/模块/优先级分布、按月完成吞吐量、平均生命周期（创建到完成的天数）。

#### 2.2 Git 数据

从 git log（时间范围内，不含 merge commit）提取：提交总数、按作者分布、按日期趋势、按 conventional commit 类型分布、代码增删行数、变更频率最高的文件 TOP 10、活跃分支数、tag 数量。

#### 2.3 代码规模（可选，当前快照）

统计主要源码文件（`.go`、`.ts`、`.vue`、`.py`、`.java` 等）的文件数和总行数，排除 `node_modules`、`vendor`、`dist` 等目录。

### 3. 输出统计报告

```

项目数据统计

项目：<project> (<role>)
统计范围：<from> ~ <to>


**需求统计**
总数：XX 个
活跃：XX 个 | 已完成：XX 个
完成率：XX%
平均生命周期：XX 天

  按状态分布：
  草稿       XX XX% 
  待评审     XX XX% 
  评审通过   XX XX% 
  开发中     XX XX% 
  测试中     XX XX% 
  已完成     XX XX% 

  按类型分布：
  后端 XX XX% 
  前端 XX XX% 
  全栈 XX XX% 

  按模块分布：
  用户模块 XX XX% 
  订单模块 XX XX% 
  支付模块 XX XX% 

  月度吞吐量（已完成需求数）：
  2026-01 X 
  2026-02 X 
  2026-03 X 



**代码活动统计**
提交总数：XX
代码变更：+XX,XXX / -X,XXX 行
变更文件：XX 个
活跃分支：XX 个
版本标签：XX 个

  按贡献者：
  张三 XX XX% 
  李四 XX XX% 
  王五 XX XX% 

  按提交类型：
  feat     XX XX% 新功能
  fix      XX XX% 修复
  refactor XX XX% 重构
  docs     XX XX% 文档
  other    XX XX% 其他

  变更最多的文件 TOP 5：
  1. path/to/file.go     XX 次 
  2. path/to/file2.go    XX 次 
  3. path/to/file3.ts    XX 次 
  4. path/to/file4.go    XX 次 
  5. path/to/file5.vue   XX 次 

  每周提交趋势：
  第 1 周 (03/01-03/07) XX 
  第 2 周 (03/08-03/14) XX 
  第 3 周 (03/15-03/21) XX 
  第 4 周 (03/22-03/26) XX 



**代码规模（当前）**
源代码文件：XX 个
代码行数：~XX,XXX 行



**相关命令：**
- /pm:weekly            生成周报
- /pm:risk              风险扫描
- /pm:stats --from=<日期>  指定起始时间
```

### 4. 提供保存选项

询问是否保存到 `docs/reports/stats/<today>.md`。

---

## 无数据处理

| 场景 | 处理方式 |
|------|---------|
| 无需求数据 | 跳过需求统计章节，仅展示 Git 和代码数据 |
| 无 Git 记录 | 跳过代码活动章节 |
| 指定范围内无数据 | 提示范围内无活动，建议调整范围 |
| 无代码文件 | 跳过代码规模章节 |

## 用户输入

$ARGUMENTS
