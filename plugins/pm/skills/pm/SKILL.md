---
name: pm
description: 项目管理助手 - 项目概况仪表盘和子命令入口
---

# 项目管理助手

> **Audience:** Product Manager

项目管理主入口，展示项目概况仪表盘，或路由到子命令。

## 命令格式

```
/pm [子命令] [参数]
```

## 子命令

| 子命令 | 说明 | 示例 |
|-------|------|------|
| (空) | 项目概况仪表盘 | `/pm` |
| `weekly` | 周报 | `/pm:weekly` |
| `monthly` | 月报 | `/pm:monthly` |
| `milestone` | 里程碑总结 | `/pm:milestone v1.6.0` |
| `stats` | 项目数据统计 | `/pm:stats` |
| `progress` | 项目总进度 | `/pm:progress` |
| `plan` | 生成方案文档 | `/pm:plan 排期方案` |
| `risk` | 风险扫描 | `/pm:risk` |
| `brief` | 项目简介 | `/pm:brief --lang=en` |
| `standup` | 站会摘要 | `/pm:standup` |
| `ask` | 自由提问 | `/pm:ask 还有几个需求没完成？` |
| `export` | 导出上次内容 | `/pm:export --format=md` |
| `help` | 使用帮助 | `/pm:help` |

---

## 执行流程（仪表盘模式）

当不带子命令执行 `/pm` 时，展示项目概况仪表盘。

### 1. 解析需求数据路径

参考 `_common.md` 的路径解析规则。

### 2. 采集数据

并行采集以下数据：

```python
# 需求数据
reqs = collect_requirements()

# PRD 数据
prd = collect_prd()

# Git 数据（最近 30 天）
git = collect_git_stats(from_date=thirty_days_ago)

# 模块数据
modules = collect_modules()

# 插件版本
version = read_plugin_json("version")  # <plugin-path>/.codex-plugin/plugin.json
```

### 3. 计算统计指标

```python
# 需求统计
active_reqs = [r for r in reqs if not r["is_completed"]]
completed_reqs = [r for r in reqs if r["is_completed"]]

# 按状态分组
status_groups = group_by(active_reqs, "status")

# 完成率
total = len(reqs)
done = len(completed_reqs)
completion_rate = f"{done}/{total}" if total > 0 else "暂无需求"

# 本周完成
this_week_done = [r for r in completed_reqs
                  if r["updated"] >= this_monday()]

# 风险项：超过 7 天未更新的活跃需求
stale_reqs = [r for r in active_reqs
              if days_since(r["updated"]) > 7]
```

### 4. 展示仪表盘

```

项目管理助手 v<version>

项目：<project> (<role>) | 日期：YYYY-MM-DD


**项目概览**
需求总数：XX 个（活跃 XX / 已完成 XX）
完成率：XX%
本周完成：X 个
PRD 完善度：X/X 章节

**需求状态分布**
草稿：X 个
待评审：X 个
评审通过：X 个
开发中：X 个
测试中：X 个
已完成：X 个（总计）

**近 30 天代码活动**
提交次数：XX
代码变更：+XXX / -XXX 行
活跃分支：XX 个
贡献者：XX 人

关注项
**严重** 超过 7 天未更新：REQ-XXX <标题>
**警告** 阻塞中：REQ-XXX <标题>（原因）
**提示** 即将完成：REQ-XXX <标题>（测试中）

**模块概览**
用户模块：X 个需求（X 活跃）
订单模块：X 个需求（X 活跃）
支付模块：X 个需求（X 活跃）



**可用命令：**
- /pm:weekly          生成本周周报
- /pm:stats           查看详细统计
- /pm:risk            风险扫描
- /pm:progress        项目总进度
- /pm:ask <问题>      自由提问
- /pm:help            查看所有命令
```

### 5. 无数据时的提示

```

项目管理助手 v<version>


未检测到需求数据

可能原因：
1. 尚未初始化需求项目 → /req:init <project-name>
2. 尚未创建任何需求 → /req:new <标题>
3. 未绑定需求项目 → /req:use <project-name>

Git 仓库数据仍可使用：
- /pm:stats   查看 Git 统计
- /pm:ask     自由提问
```

---

## 边界情况处理

| 场景 | 处理方式 |
|------|---------|
| 无需求数据但有 Git 记录 | 仅展示 Git 相关指标，需求部分提示未初始化 |
| 无 PRD | PRD 完善度显示「未创建」 |
| readonly 仓库 | 从缓存读取数据，标注数据来源 |
| 无 Git 仓库 | 跳过 Git 相关指标 |

## 用户输入

$ARGUMENTS
