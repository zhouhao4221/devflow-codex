---
name: ask
description: 自由提问 - 基于项目数据回答任何项目相关问题
---

# 自由提问

> **Audience:** Product Manager

基于项目的 PRD、需求文档、Git 记录等数据，回答任何项目相关问题。

## 命令格式

```
/pm:ask <问题>
```

**示例：**
- `/pm:ask 还有几个需求没完成？`
- `/pm:ask 上周谁的提交最多？`
- `/pm:ask 哪个模块的需求最多？`
- `/pm:ask 最近一个版本包含了哪些功能？`
- `/pm:ask 项目的技术栈是什么？`
- `/pm:ask 帮我写一段给客户的进展邮件`

---

## 执行流程

### 1. 分析问题意图

根据问题关键词判断需要哪些数据：

```python
question = args.question

# 关键词 → 数据源映射
if matches(question, ["需求", "进度", "完成", "待办", "状态"]):
    data["reqs"] = collect_requirements()

if matches(question, ["提交", "代码", "贡献", "git", "变更"]):
    data["git"] = collect_git_stats()

if matches(question, ["模块", "功能", "架构"]):
    data["modules"] = collect_modules()

if matches(question, ["PRD", "产品", "愿景", "规划", "技术栈"]):
    data["prd"] = collect_prd()

if matches(question, ["版本", "发布", "tag", "里程碑"]):
    data["tags"] = git_tags()

# 无法判断时，采集全部数据
if not data:
    data = collect_all()
```

### 2. AI 基于数据回答

**回答原则：**
- 必须基于实际项目数据，不编造
- 给出具体数字和引用
- 如果数据不足以回答，明确说明缺少什么
- 区分事实和推测

### 3. 输出格式

自由格式，根据问题类型调整：
- 数量类问题 → 简短数字回答 + 详细列表
- 分析类问题 → 结构化分析
- 生成类问题 → 直接生成内容
- 对比类问题 → 表格对比

```

/pm:ask


Q: <用户问题>

A: <基于项目数据的回答>


```

## 用户输入

$ARGUMENTS
