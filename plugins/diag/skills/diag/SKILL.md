---
name: diag
description: 生产诊断插件 - 列出 init / diagnose / audit 子命令
---

# Diag - 生产诊断插件

**只读拉日志 · AI 解析堆栈 · 关联代码 · 给修复建议**

与 [claude-safe-ops](https://github.com/zhouhao4221/claude-safe-ops) 互补：它管**执行类**运维动作，本插件管**只读诊断**。

---

## 子命令

| 命令 | 用途 |
|---|---|
| `/diag:init` | 初始化 `~/.devflow-diag/` + 生成服务清单模板 + 依赖检查 |
| `/diag:diagnose <报错描述> [--service=<name>]` | 报错定位主流程（SSH 拉日志 → 堆栈解析 → 代码关联 → 修复建议） |
| `/diag:audit [--host] [--service] [--from] [--to] [--limit]` | 审计日志查询（默认近 7 天） |

---

## 快速开始

```bash
/diag:init                              # 初始化配置
# 编辑 ~/.devflow-diag/config/services.yaml，登记真实服务
/diag:diagnose 订单接口刚才报 500        # 开始诊断
```

---

## 核心边界

- ✅ **读**：`tail / head / cat / grep / awk / sed / less / wc / find -name / ls / ps / df / free / uptime` 等只读命令
- ❌ **写**：禁止 `rm / mv / cp / chmod / 重定向 / 服务控制 / 包管理 / DB 写 / 一切修改类操作`
- ❌ **代码**：修复建议以文字形式给出，插件**不触发** Edit / Write 改动仓库

所有 SSH 操作都会被 5 类风控校验，并落 JSONL 审计。
