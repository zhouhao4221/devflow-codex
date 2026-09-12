# 公共逻辑参考 - 分支策略

> 此文档定义分支策略配置（`branchStrategy`）的结构、预设和读取规则。
>

## 分支策略配置

分支策略存储在 `.devflow/settings.json` 的 `branchStrategy` 字段中，通过 `/req:branch init` 初始化。`giteaToken` 敏感字段单独存入 `.devflow/settings.local.json`（不纳入 git）。

### 配置结构

`settings.json`（团队共享，纳入 git）：
```jsonc
{
  "branchStrategy": {
    "model": "github-flow",       // github-flow | git-flow | trunk-based
    "repoType": "github",         // github | gitea | other（仓库托管类型）
    "giteaUrl": null,             // Gitea 实例地址（repoType=gitea 时必填，如 https://git.example.com）
    "mainBranch": "main",         // 生产分支
    "developBranch": null,        // git-flow 模式下的开发分支
    "featurePrefix": "feat/",     // REQ-XXX 分支前缀
    "fixPrefix": "fix/",          // QUICK-XXX 分支前缀
    "hotfixPrefix": "hotfix/",    // 紧急修复前缀
    "branchFrom": "main",         // 功能/修复分支的拉取基准
    "mergeTarget": "main",        // 默认合并目标
    "mergeMethod": "merge",       // 合并方式：merge | squash | rebase
    "deleteBranchAfterMerge": true
  }
}
```

`settings.local.json`（本地私有，禁止提交）：
```jsonc
{
  "giteaToken": null             // Gitea API Token（tea 未配置时的 curl 回退凭据）
}
```

### 三种策略预设

| 配置项 | GitHub Flow | Git Flow | Trunk-Based |
|--------|------------|----------|-------------|
| branchFrom | main | develop | main |
| mergeTarget | main | develop | main |
| developBranch | null | develop | null |
| hotfix 合并目标 | main | main + develop | main |

### 读取规则

1. 先读 `.devflow/settings.json` 的 `branchStrategy`，再用 `.devflow/settings.local.json` 中同名字段覆盖（`giteaToken` 以 local 为准）
2. **有配置** → 使用配置值
3. **无配置** → 使用默认行为（`feat/`、`fix/` 前缀，自动检测主分支）

### 各命令的策略消费

| 命令 | 读取的配置 | 用途 |
|------|-----------|------|
| `/req:dev` | `branchFrom`、`featurePrefix`、`fixPrefix` | 创建分支时的基准和前缀 |
| `/req:commit` | `mainBranch`、`developBranch` | 检查当前分支是否合规 |
| `/req:done` | `mergeTarget`、`deleteBranchAfterMerge`、`repoType`、`giteaUrl` | 合并提醒、PR 创建（Gitea）|
| `/req:branch hotfix` | `mainBranch`、`hotfixPrefix` | 从主分支创建紧急修复 |
| `/req:branch status` | `repoType` | 显示仓库托管类型 |
