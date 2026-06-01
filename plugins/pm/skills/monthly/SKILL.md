---
name: monthly
description: 月报 - 月度工作总结与统计分析
---

# 生成月报

> **Audience:** Product Manager

从需求文档和 Git 记录生成月度工作总结，包含本月成果、数据统计、趋势分析和下月计划。

## 命令格式

```
/pm:monthly [--month=YYYY-MM] [--save]
```

**参数说明：**
- `--month`：可选，指定月份，默认当月
- `--save`：可选，直接保存不询问

**示例：**
- `/pm:monthly` — 当月月报
- `/pm:monthly --month=2026-02` — 2 月月报

---

## 执行流程

### 1. 确定时间范围

```python
if args.month:
    year, month = args.month.split('-')
    from_date = f"{year}-{month}-01"
    to_date = last_day_of_month(year, month)
else:
    from_date = today.replace(day=1).isoformat()
    to_date = today.isoformat()
```

### 2. 采集数据

与 weekly 类似，但范围为整月：
- 本月完成的需求
- 本月新创建的需求
- 本月 Git 统计（提交、变更、贡献者）
- 与上月的对比数据

### 3. 输出月报

```

项目月报

项目：<project> | 月份：YYYY-MM


## 月度总结

本月聚焦 XX 模块开发，完成 X 个需求，新建 X 个需求。
代码提交 XX 次，净增 +X,XXX 行代码。

## 本月完成

| 编号 | 标题 | 类型 | 完成日期 | 提交数 |
|------|------|------|---------|--------|
| REQ-005 | 用户积分兑换 | 后端 | 03-22 | 12 |
| QUICK-003 | 修复登录超时 | 全栈 | 03-20 | 3 |

## 进行中

| 编号 | 标题 | 状态 | 进度 |
|------|------|------|------|
| REQ-006 | 订单导出 | 开发中 | 60% |
| REQ-007 | 消息通知 | 测试中 | 90% |

## 数据统计

| 指标 | 本月 | 上月 | 趋势 |
|------|------|------|------|
| 需求完成 | X | X | ↑/↓/→ |
| 需求新建 | X | X | ↑/↓/→ |
| 提交次数 | XX | XX | ↑/↓/→ |
| 代码变更 | +X,XXX/-XXX | +X,XXX/-XXX | ↑/↓/→ |
| 贡献者 | X | X | → |

## 风险与问题

- 本月遇到的阻塞和解决方案
- 未解决的遗留问题

## 下月计划

- 基于活跃需求推导的下月重点


*由 /pm:monthly 自动生成 · YYYY-MM-DD*
```

### 4. 提供保存选项

```python
month_str = args.month or today.strftime("%Y-%m")
offer_save(content, f"docs/reports/monthly/{month_str}.md")
```

## 用户输入

$ARGUMENTS
