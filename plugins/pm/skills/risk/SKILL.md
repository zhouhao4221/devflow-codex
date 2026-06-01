---
name: risk
description: 风险扫描 - 自动检测项目中的延期、阻塞和异常情况
---

# 风险扫描

> **Audience:** Product Manager

自动扫描项目数据，识别延期需求、长期未更新分支、异常提交模式等风险信号。

## 命令格式

```
/pm:risk [--save]
```

---

## 执行流程

### 1. 采集数据

```python
reqs = collect_requirements()
git = collect_git_stats(from_date=thirty_days_ago)
```

### 2. 风险检测规则

#### 2.1 需求层面

```python
risks = []

for req in active_reqs:
    days_inactive = days_since(req["updated"])

    # 严重：超过 14 天未更新
    if days_inactive > 14:
        risks.append({
            "level": "critical",
            "type": "stale",
            "req": req["id"],
            "title": req["title"],
            "detail": f"已 {days_inactive} 天未更新，状态停留在 {req['status']}",
        })

    # 警告：超过 7 天未更新
    elif days_inactive > 7:
        risks.append({
            "level": "warning",
            "type": "slow",
            "req": req["id"],
            "title": req["title"],
            "detail": f"已 {days_inactive} 天未更新",
        })

    # 警告：草稿超过 5 天未进入评审
    if req["status"] == "草稿" and days_since(req["created"]) > 5:
        risks.append({
            "level": "warning",
            "type": "draft_stuck",
            "req": req["id"],
            "title": req["title"],
            "detail": f"草稿已创建 {days_since(req['created'])} 天，建议尽快评审",
        })

    # 严重：开发中但功能进度为 0
    if req["status"] == "开发中" and req["progress"] == "0/X":
        risks.append({
            "level": "critical",
            "type": "no_progress",
            "req": req["id"],
            "title": req["title"],
            "detail": "状态为开发中但功能进度为 0，可能被阻塞",
        })
```

#### 2.2 代码层面

```python
# 警告：长期未合并的分支（超过 14 天）
for branch in git["active_branches"]:
    if branch.last_commit_days > 14 and not branch.is_merged:
        risks.append({
            "level": "warning",
            "type": "stale_branch",
            "detail": f"分支 {branch.name} 已 {branch.last_commit_days} 天无提交",
        })

# 警告：频繁修复同一文件（7 天内修复超过 3 次）
hot_fix_files = find_frequently_fixed_files(days=7, threshold=3)
for file in hot_fix_files:
    risks.append({
        "level": "warning",
        "type": "hot_file",
        "detail": f"{file.path} 近 7 天有 {file.fix_count} 次修复提交",
    })

# 提示：提交频率异常下降
if git["this_week_commits"] < git["avg_weekly_commits"] * 0.3:
    risks.append({
        "level": "info",
        "type": "low_activity",
        "detail": f"本周提交 {git['this_week_commits']} 次，低于平均 {git['avg_weekly_commits']} 次",
    })
```

#### 2.3 流程层面

```python
# 警告：有需求跳过评审直接开发
for req in reqs:
    if req["type"].startswith("REQ") and req["status"] == "开发中":
        if not has_review_record(req):
            risks.append({
                "level": "warning",
                "type": "skip_review",
                "req": req["id"],
                "detail": "未找到评审记录，可能跳过了评审环节",
            })
```

### 3. 输出风险报告

```

项目风险扫描

项目：<project> | 扫描日期：YYYY-MM-DD


**风险概览**
**严重**：X 项
**警告**：X 项
**提示**：X 项
总计：X 项风险



**严重**

  1. REQ-003 订单导出 — 停滞 18 天
     状态：开发中（功能进度 2/6）
     最后更新：2026-03-08
     建议：确认是否被阻塞，考虑拆分或重新排期

  2. REQ-007 消息通知 — 开发中无进度
     状态：开发中（功能进度 0/5）
     进入开发：2026-03-20
     建议：确认是否遇到技术障碍



**警告**

  3. REQ-008 支付对账 — 草稿滞留 8 天
     创建日期：2026-03-18
     建议：尽快安排评审或调整优先级

  4. 分支 feat/REQ-003-order-export — 16 天无提交
     最后提交：2026-03-10
     建议：确认分支状态，考虑是否需要关闭

  5. internal/oms/biz/order_biz.go — 频繁修复
     近 7 天有 4 次 fix 提交
     建议：检查该模块是否需要重构



**提示**

  6. 本周提交活动偏低
     本周提交 5 次，周均 23 次
     可能原因：节假日、会议集中、需求评审阶段



**建议操作：**
- /pm:stats --from=2026-03-01  查看本月详细统计
- /req:status REQ-003          查看停滞需求详情
- /pm:weekly                   生成周报梳理进展
```

### 4. 提供保存选项

```python
offer_save(content, f"docs/reports/risk/{today}.md")
```

---

## 风险级别定义

| 级别 | 含义 | 典型场景 |
|------|------|---------|
| **严重** | 需要立即关注 | 需求停滞 14+ 天、开发中无进度 |
| **警告** | 需要近期处理 | 7+ 天未更新、草稿滞留、分支过期 |
| **提示** | 值得留意 | 活动量下降、代码热点 |

## 无风险时

```

项目风险扫描 -- 一切正常

项目：<project> | 扫描日期：YYYY-MM-DD

未检测到风险项。项目运行健康。

**健康指标：**
活跃需求均有近期更新
无过期分支
提交频率正常
无频繁修复热点

```

## 用户输入

$ARGUMENTS
