---
name: diagnose
description: 生产报错定位 - SSH 拉日志 → AI 解析堆栈 → 本地代码关联 → 修复建议
---

# /diag:diagnose - 报错定位

通过自然语言描述报错 → 插件拉取生产日志 → AI 识别堆栈 → 在本地代码关联源码 → 输出诊断报告和修复建议。

**全程只读**，所有 SSH 命令都会经过 5 类 Hook 校验，审计落盘。

---

## 参数

| 参数 | 说明 | 默认 |
|---|---|---|
| `<报错描述>` | 自然语言描述（必填），如 "订单提交接口刚才报 500" | - |
| `--service=<name>` | 指定服务（可选，否则让用户选） | - |
| `--lines=<N>` | 拉取日志的行数（tail -n N） | 2000 |
| `--pattern=<regex>` | grep 过滤的正则，覆盖默认 | `ERROR\|Exception\|FATAL\|PANIC` |

---

## 执行流程

### 0. Session 初始化

每次执行 `/diag:diagnose` 时，在读取服务清单前先完成 session 管理：

1. 清理本地超过 2h 的遗留 session 文件（`$DIAG_HOME/tmp/.current-session`、`runtime/tmp-*.json`）
2. 若上一轮 session 文件仍存在，读取旧 session id，对本次诊断涉及的每台主机各执行一次远端清理（`rm -f /tmp/claude-diag-<OLD_SESSION>-*`）；此命令通过 write-guard 的 tmp 白名单，审计落盘
3. 生成新 session id（8 位十六进制），写入本地 session 文件

### 1. 读取服务清单

调用 `services-config.sh list` 获取服务列表。配置文件不存在 → 提示 `/diag:init`，终止。

### 2. 选择目标服务

- `--service` 已指定 → 校验存在后使用
- 未指定 → 向用户展示服务列表，让用户选（单选或"全部"）

也接受自然语言匹配：用户描述里提到 "订单接口"，AI 可以匹配 `order-api` 服务，展示后让用户确认。

### 3. 构造 SSH 拉日志命令

从选中服务读取：
- `host`
- `log_paths`（数组）
- `language_hint`（可选，传给 stack-analyzer 技能作识别提示）

**命令模板**（每条日志单独执行一次）：

```bash
# 标准只读（优先使用）
ssh <host> "tail -n <lines> <log_path> | grep -B2 -A 30 -E '<pattern>'"

# 落远端临时文件（数据量大、需要多步处理时使用）
ssh <host> "tail -n <lines> <log_path> | grep -E '<pattern>' | tee -a /tmp/claude-diag-<session>-<topic>.log"
# 之后读回
ssh <host> "cat /tmp/claude-diag-<session>-<topic>.log"
# 清理（诊断结束时执行）
ssh <host> "rm -f /tmp/claude-diag-<session>-*"
```

**命令约束**：
- 优先纯 stream（stdout 回本地），避免不必要的远端写入
- 远端临时文件路径必须以 `/tmp/claude-diag-<session>-` 开头（`<session>` 即当前 session id）
- 写入只允许 `tee -a`（append），禁止裸 `>` / `>>`
- 清理只允许 `rm -f /tmp/claude-diag-<session>-*`，禁止 `-r` / `-rf`
- 禁止在 `/tmp` 下创建子目录
- 生产机 `/tmp` 可能有容量或 noexec 限制；若 `tee -a` 失败，降级到纯 stream 模式
- 目标 host 必须在 `services.yaml` 登记

### 4. 执行 SSH 拉日志

通过 Bash 工具执行构造好的命令。Hook 链会依次校验：
- `validate-hooks`（首次校验完整性）
- `host-whitelist`（host 在白名单）
- `command-whitelist`（每个 verb 在白名单）
- `write-guard`（无写操作）

若任一 Hook 拒绝 → 展示拒绝理由给用户，**不要**尝试绕过（如删选项、改写命令），而是向用户说明并询问是否调整需求。

### 5. AI 识别堆栈（stack-analyzer 技能）

日志拉回后，由 `stack-analyzer` 技能（自动触发）根据 `language_hint` 识别堆栈格式，抽取：
- 异常类 / 错误类型
- 错误消息
- 堆栈帧（文件、行号、方法名）

### 6. 本地代码关联

对每个堆栈帧：
- 用 `Grep` 在当前仓库按 类名 / 方法名 / 文件名 查找
- 用 `Read` 查看命中位置的前后 15 行，理解上下文

若堆栈帧对应的源码在当前仓库找不到 → 标注"**本仓库外**"，不强行定位。

### 7. 生成诊断报告

**固定模板**：

```
原因：<异常类型> - <根本原因推断>

相关代码：
  - <file_path>:<line> - <方法/类>（<匹配方式：精确匹配 / 模糊匹配 / 本仓库外>）
  - ...

完整堆栈：
  <堆栈前 5-10 帧>

修复建议：
  <具体到文件/函数的文字建议；必要时给出代码片段，但不自动应用>

审计：
  - 主机：<host>
  - 拉取日志：<log_paths>
  - SSH 命令：<3-5 条>
  - 审计记录：~/.claude-diag/audit/command_audit-<date>.jsonl

未改动任何远程资源和本地代码。如需应用修复，你自己决定并手动执行。

Session 清理：
  - 远端临时文件：/tmp/claude-diag-<session>-* 已清理 / 无遗留
  - 本地 session 文件：~/.claude-diag/tmp/.current-session
```

### 8. 清理远端临时文件

诊断结束后（输出报告之前），对本次涉及的每台主机执行清理：

```bash
ssh <host> "rm -f /tmp/claude-diag-<session>-*"
```

**条件**：仅在本次诊断过程中确实用了 `tee -a` 写入过远端临时文件时执行；纯 stream 模式无需清理。

清理失败不中断诊断报告输出，但在 Session 清理一栏标注"⚠️ 清理失败，请手动执行"。

### 9. 可选：追查链路

若用户要求深入（"再看下 user.log"），按同样流程再拉一次，不主动扩大范围。

---

## 边界

- **只拉日志**：本期不查 DB、不摸文件内容、不看进程
- **不改代码**：修复建议纯文字，不触发 Edit / Write
- **不递归**：Claude 不应在本次会话中"为了调查而 SSH 到其他未登记主机"
- **审计友好**：所有 SSH 命令走 Bash 工具，自动被 `audit-log.sh` 记录

---

## 故障排查

| 现象 | 可能原因 |
|---|---|
| Hook 拒绝 host | 服务未在 `services.yaml` 登记 → `/diag:init` 补充 |
| Hook 拒绝命令 | AI 构造了非白名单命令，需要调整（如不要用 `tee`） |
| 拉不到日志 | SSH 本身不通（key / agent / 网络）→ 先本地测 `ssh <host> echo ok` |
| 堆栈识别不准 | 服务设置 `language_hint` 后重试；或把日志片段粘给用户让其确认 |
| 本地找不到代码 | 堆栈属于第三方依赖或其他仓库，标注后跳过，不要硬猜 |
