---
name: export
description: |
  导出内容 - 将 pm 生成的内容保存到 docs/reports/
---

# 导出内容

> **Audience:** Product Manager

将最近一次 pm 命令生成的内容保存到 `docs/reports/` 目录。
也可以直接指定要执行的命令并保存结果。

## 命令格式

```
/pm:export [命令名] [--format=md] [--path=自定义路径]
```

**参数说明：**
- `命令名`：可选，指定要执行并导出的命令（如 `weekly`、`stats`）
- `--format`：可选，输出格式，默认 md
- `--path`：可选，自定义保存路径

**示例：**
- `/pm:export weekly` — 生成周报并直接保存
- `/pm:export stats --from=2026-03-01` — 生成统计并保存
- `/pm:export --path=给客户的报告.md` — 保存到自定义路径

---

## 执行流程

### 1. 确定内容来源

```python
if args.command:
    # 执行指定命令获取内容
    content = execute_pm_command(args.command, args)
else:
    # 提示用户指定命令
    print("请指定要导出的命令：")
    print("  /pm:export weekly")
    print("  /pm:export stats")
    print("  /pm:export progress")
    exit()
```

### 2. 确定保存路径

```python
if args.path:
    save_path = args.path
else:
    # 按命令类型自动生成路径
    paths = {
        "weekly": f"docs/reports/weekly/{to_date}.md",
        "monthly": f"docs/reports/monthly/{month}.md",
        "milestone": f"docs/reports/milestone/{version}.md",
        "stats": f"docs/reports/stats/{today}.md",
        "progress": f"docs/reports/progress/{today}.md",
        "risk": f"docs/reports/risk/{today}.md",
        "plan": f"docs/reports/plans/{topic_slug}.md",
        "brief": "docs/reports/brief.md",
    }
    save_path = paths.get(args.command, f"docs/reports/custom/{today}.md")
```

### 3. 保存文件

```python
mkdir_p(dirname(save_path))
write_file(save_path, content)
print(f"已保存到 {save_path}")
```

### 4. 输出确认

```
导出成功

文件路径：docs/reports/weekly/2026-03-26.md
内容类型：周报
生成日期：2026-03-26

**后续操作：**
- git add docs/reports/  提交到版本控制
- /pm:help              查看其他命令
```

## 用户输入

$ARGUMENTS
