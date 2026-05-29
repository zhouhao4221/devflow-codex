---
name: init
description: |
  初始化 Diag 插件 - 创建 ~/.claude-diag/ 配置目录 + 服务清单模板 + 依赖检查
---

# /diag:init - 初始化 Diag 插件

首次使用 Diag 插件时执行，完成以下事项：

1. **依赖检查**：`python3`、`jq`、`ssh`、`yq` 或 `pyyaml`
2. **创建目录**：`~/.claude-diag/{config,audit}/`（700 权限）
3. **生成配置模板**：`~/.claude-diag/config/services.yaml`（600 权限）
4. **引导配置**：让用户将真实服务登记到 `services.yaml`
5. **配置校验**：确保必填字段齐全
6. **（可选）空跑测试**：SSH `echo ok` 验证 Hook 链路

---

## 执行流程

### 1. 运行初始化脚本

调用 `init-diag.sh`，该脚本会：
- 检查 `python3 / jq / ssh / yq(或 pyyaml)` 是否可用，缺失则终止
- 创建 `~/.claude-diag/config/` 和 `~/.claude-diag/audit/`
- 若 `services.yaml` 不存在，则从模板拷贝（已存在时不覆盖）
- 打印目录结构和下一步指引

### 2. 创建项目 Runbook 目录

在当前项目的 `docs/runbooks/` 创建事故处理文档骨架，仅当文件不存在时创建：

| 文件 | 用途 |
|------|------|
| `db-slow-query.md` | 数据库慢查询处理 |
| `oom.md` | 内存溢出处理 |
| `5xx-spike.md` | 接口报错飙升处理 |
| `deployment-rollback.md` | 部署回滚流程 |

每个文件使用统一的 5 节骨架，节内容留空，在 `/diag:diagnose` 诊断完事故后由 AI 协作补写：

```markdown
# <事故类型>

> <一行用途说明>

## 什么时候用

<!-- 触发条件和典型症状 -->

## 必备输入

<!-- 开始诊断前需要收集的信息（日志、监控指标、错误码等） -->

## 触发方式

<!-- /diag:diagnose 命令模板 + 需要提供的上下文 -->

## 优质输出标准

<!-- 定位到根因、给出可执行的修复步骤 -->

## 常见失败模式

| 问题 | 原因 | 解决方案 |
|------|------|----------|
```

若不在 git 仓库目录下运行（`git rev-parse --is-inside-work-tree` 失败），跳过此步骤。

### 3. 引导用户编辑服务清单

脚本结束后向用户展示：

```
✅ 已创建配置模板：~/.claude-diag/config/services.yaml

请现在告诉我你的服务信息，我帮你填写（或你自己编辑后回复"已填写"）：

- 服务名（如 order-api）：
- 主机（对应 ~/.ssh/config 里的 Host 名 或 user@ip）：
- 日志路径（可以多条）：
- 语言栈（可选，java/node/python/go/ruby/php）：
```

**用户配合方式**：
- **方式 A（对话录入）**：用户说"服务名 order-api，主机 prod-web-01，日志 /var/log/app/order.log"，AI 用 `Edit` 工具改 `~/.claude-diag/config/services.yaml`
- **方式 B（自行编辑）**：用户说"我自己编辑"，AI 等待用户说"已填写"后继续校验

### 4. 校验配置

```bash
bash "${CLAUDE_PLUGIN_ROOT}/scripts/services-config.sh" validate
```

- 通过 → 展示服务数量
- 失败 → 展示具体错误（缺字段 / 重名 / language_hint 非法），让用户修复后重试

### 5. （可选）Hook 空跑测试

询问用户是否跑一次空测试：

```
是否执行一次空测试？（SSH <host> 'echo ok' 验证 Hook 链路是否生效）  [Y/n]
```

若同意：
1. 从 `services.yaml` 取第一个服务的 host
2. 执行 `ssh <host> 'echo ok'`（应被 Hook 放行，因 echo 在白名单）
3. 展示退出码和 `~/.claude-diag/audit/` 下的 JSONL 条目，证明链路通

**注意**：本期不强制执行空测试，用户拒绝即跳过。

### 6. 输出总结

```
✅ Diag 插件初始化完成

配置：~/.claude-diag/config/services.yaml（2 个服务）
审计：~/.claude-diag/audit/
Runbook：docs/runbooks/（4 个骨架文件，诊断完事故后补写内容）

下一步：
- /diag:diagnose <报错描述>   开始诊断
- /diag:audit                 查审计日志
```

---

## 边界

- 只在 **primary** 仓库意义上执行（插件无 primary/readonly 区分，但应在用户本机执行，不要在 CI/CD 环境）
- `~/.claude-diag/` 不纳入任何仓库；多机协作时，每台机器独立 init

## 故障排查

| 问题 | 诊断 |
|---|---|
| `yq/pyyaml 都没装` | 选一：`brew install yq` 或 `pip3 install pyyaml` |
| `services.yaml 已存在` | 脚本不覆盖，可手动 `rm ~/.claude-diag/config/services.yaml` 后重 init |
| `Hook 不生效` | 重启 Claude Code 让插件加载；检查 `.claude/settings.local.json` 的 `enabledPlugins.diag@devflow: true` |
