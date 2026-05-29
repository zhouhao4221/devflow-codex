---
name: audit
description: |
  查询 Diag 审计日志 - 按主机/服务/时间过滤
---

# /diag:audit - 审计查询

查询 Diag 插件的 SSH 命令审计日志。审计记录按日切分，保留 30 天。

---

## 参数

| 参数 | 说明 | 默认 |
|---|---|---|
| `--host=<name>` | 按目标主机过滤 | 全部 |
| `--service=<name>` | 按服务名过滤 | 全部 |
| `--from=YYYY-MM-DD` | 起始日期（本地时区） | 7 天前 |
| `--to=YYYY-MM-DD` | 截止日期 | 今天 |
| `--limit=<N>` | 最多输出条数 | 50 |
| `--temp-files` | 只显示有远端临时文件写入的记录 | 关闭 |

---

## 执行流程

### 1. 扫描审计文件

```bash
ls ~/.claude-diag/audit/command_audit-*.jsonl 2>/dev/null
```

若目录不存在或无文件 → 提示"暂无审计记录，`/diag:init` 初始化后使用 `/diag:diagnose` 会产生记录"。

### 2. 按日期过滤文件

审计文件名是 `command_audit-YYYY-MM-DD.jsonl`，按 `--from` / `--to` 范围筛选要读的文件。

默认 `--from` = 今天前 7 天，`--to` = 今天。

### 3. 读取并过滤记录

```bash
cat ~/.claude-diag/audit/command_audit-{dates}.jsonl | jq -c '
    select(
        (.host == "<host>" or "<host>" == "") and
        (.service == "<service>" or "<service>" == "")
    )
' | tail -n <limit>
```

字段：`timestamp / session_id / diag_session_id / operator / host / service / command / exit_code / stdout_length / log_snippet_hash / tmp_write / hooks_passed`

`--temp-files` 时用 jq 过滤 `tmp_write != null`：

```bash
cat ... | jq -c 'select(.tmp_write != null)'
```

### 4. 格式化输出

表格形式（默认）：

```
Diag 审计（2026-04-13 至 2026-04-20，共 23 条）

时间                    主机            服务        命令                                        退出码
2026-04-20T02:30:15Z   prod-web-01    order-api   ssh prod-web-01 tail -n 2000 /v/l/order.l    0
2026-04-20T02:31:08Z   prod-web-01    order-api   ssh prod-web-01 grep ERROR /v/l/order.l      0
2026-04-19T22:05:42Z   prod-web-02    user-svc    ssh prod-web-02 tail -n 500 /v/l/user.log    0
...

完整记录：cat ~/.claude-diag/audit/command_audit-*.jsonl | jq '.'
```

聚合摘要（若记录 > 20）：
```
统计
- 主机分布：prod-web-01 (15), prod-web-02 (8)
- 服务分布：order-api (15), user-svc (8)
- 成功率：23/23 (100%)
- 高频命令：tail (18), grep (5)
```

### 5. 边界说明

- 审计日志**不含** stdout 全文（只存 SHA-256 哈希 + 字节长度），保护敏感信息
- 若审计文件损坏（无效 JSON 行），跳过该行并提示"⚠️ 第 N 行 JSON 解析失败"
- 只读查询，**不修改**审计文件

---

## 常用场景

```bash
/diag:audit                                              # 近 7 天全部
/diag:audit --host=prod-web-01                           # 指定主机
/diag:audit --service=order-api --from=2026-04-15        # 服务 + 起始日期
/diag:audit --limit=5                                    # 只看最近 5 条
/diag:audit --temp-files                                 # 只看有远端临时文件写入的记录
/diag:audit --temp-files --host=prod-web-01              # 指定主机的临时文件记录
```
