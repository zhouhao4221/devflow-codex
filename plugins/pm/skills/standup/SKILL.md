---
name: standup
description: 站会摘要 - 昨天完成、今天计划、阻塞项
---

# 站会摘要

> **Audience:** Product Manager

生成简洁的每日站会汇报内容：昨天做了什么、今天要做什么、有什么阻塞。

## 命令格式

```
/pm:standup
```

---

## 执行流程

### 1. 采集数据

```python
yesterday = today - timedelta(days=1)
# 如果昨天是周末，回溯到上周五
if yesterday.weekday() >= 5:
    yesterday = yesterday - timedelta(days=yesterday.weekday() - 4)
```

```bash
# 昨天的提交
git log --oneline --no-merges --since='$YESTERDAY' --until='$TODAY'

# 昨天变更的需求（通过文件修改时间或 git 记录）
git log --name-only --no-merges --since='$YESTERDAY' --until='$TODAY' --pretty=format: | \
  grep -E 'requirements/(active|completed)/' | sort -u
```

```python
# 当前进行中的需求
in_progress = [r for r in reqs if r["status"] in ["开发中", "测试中"]]

# 阻塞项
blocked = [r for r in in_progress if days_since(r["updated"]) > 3]
```

### 2. 输出站会摘要

```

站会摘要 · YYYY-MM-DD


**昨日完成：**
- feat: 完成订单导出模板引擎 (REQ-006)
- fix: 修复分页查询参数丢失
- test: 补充积分兑换单元测试

**今日计划：**
- REQ-006 订单导出：实现异步导出队列
- REQ-007 消息通知：跑回归测试

**阻塞/风险：**
- REQ-006 依赖第三方 SDK 版本确认（等待中）


```

**特点：**
- 极简风格，不展示统计数据
- 聚焦行动：做了什么、要做什么、卡在哪
- 通常不保存（临时内容）

### 3. 无昨日活动时

```

站会摘要 · YYYY-MM-DD


**昨日完成：**
  （无提交记录）

**今日计划：**
- REQ-006 订单导出：继续开发（进度 60%）

**阻塞/风险：**
  （无）

```

## 用户输入

$ARGUMENTS
