---
name: bug
description: |
  上报测试失败项 - 将失败场景创建为 Gitea issue
---

# 上报测试 Bug

> **Audience:** QA

将最近一次测试的失败场景上报为 Gitea issue。

## 命令格式

```
/uat:bug [module]
```

---

## 执行流程

### 1. 读取配置

从 `settings.local.json` 读取：
- `branchStrategy.repoType`：仓库类型（github / gitea）
- `branchStrategy.giteaUrl`：Gitea 地址（gitea 时必填）
- `branchStrategy.giteaToken`：Gitea token（gitea 时必填）

### 2. 找到最新报告

扫描 `docs/uat/reports/` 找最新报告文件，提取所有 `❌ FAIL` 场景。

若无失败项：
```
✅ 最近一次测试全部通过，无需上报
```

若无报告文件：
```
❌ 未找到测试报告，请先执行 /uat:run
```

### 3. 展示候选列表并询问

```
发现 3 个需上报场景：

❌ 失败（2 个）：
  1. S02 密码错误提示
     原因：表单未显示错误信息

  2. S05 退出登录后跳转
     原因：未跳转到登录页

⚠️  Console Error（1 个，功能表现正常但有 JS 异常）：
  3. S03 新增客户
     TypeError: Cannot read properties of undefined (reading 'id')

是否上报？(y/n/选择编号如 1,2,3)
```

用户可选择全部上报、部分上报或取消。

### 4. 上报 issue

**前置检查**（gitea 仓库）：
- `giteaUrl` 和 `giteaToken` 非空，否则提示：
  ```
  ❌ 未配置 giteaUrl / giteaToken
  在 settings.local.json 中配置后重试
  ```

**CLI 优先**（与 req 插件保持一致）：
- GitHub：`gh issue create`
- Gitea：优先 `tea issue create`，不可用时回退 `curl + giteaToken`

**上报范围**：`❌ FAIL` 和 `⚠️ PASS（有 console error）` 的场景都纳入上报候选，在步骤 3 展示时分组标注。

**issue 正文**：

```
## 测试场景
- 模块：<module>
- 场景：S0N <场景名称>
- 测试日期：YYYY-MM-DD
- 结果：❌ FAIL / ⚠️ PASS（有 console error）

## 失败步骤
<失败步骤描述，⚠️ PASS 时填「步骤均通过，但有 console error」>

## 预期结果
<预期断言>

## 实际结果
<失败原因，⚠️ PASS 时填「功能表现正常，但 console 有以下报错」>

## Console Errors
<本场景捕获的 console error，无则省略此节>

---
由 /uat:bug 自动生成
```

> 截图不写在正文里，创建 issue 后单独上传（见步骤 5）。

### 5. 上传截图附件

issue 创建成功后，检查该场景是否有对应截图（`docs/uat/screenshots/` 下匹配场景 ID 的文件）。有则上传，无则跳过。

**GitHub**（`repoType=github`）：

```bash
# 获取当前仓库
REPO=$(gh repo view --json owner,name -q '"\\(.owner.login)/\\(.name)"')

# 上传截图到 GitHub，获取可访问 URL
UPLOAD_RESPONSE=$(curl -s -X POST \
  "https://uploads.github.com/repos/$REPO/issues/assets" \
  -H "Authorization: token $(gh auth token)" \
  -H "Content-Type: image/png" \
  --data-binary "@<截图路径>")
IMG_URL=$(echo $UPLOAD_RESPONSE | jq -r '.url // empty')

# 追加图片评论到 issue
gh issue comment <issue_number> --body "![截图]($IMG_URL)"
```

若 upload 失败（非 2xx）：追加一条评论写明截图本地路径，提示手动上传。

**Gitea**（`repoType=gitea`）：

```bash
# 上传附件到 issue
curl -s -X POST "$GITEA_URL/api/v1/repos/$OWNER/$REPO/issues/$ISSUE_NUM/assets" \
  -H "Authorization: token $GITEA_TOKEN" \
  -F "attachment=@<截图路径>"
```

附件上传后 Gitea 自动在 issue 页面展示，无需额外操作。

若 `tea` CLI 支持附件上传则优先 `tea`，否则回退 `curl`。

### 6. 输出结果

```
✅ 已创建 2 个 issue：

  #42 [UAT] 用户登录 - S02 密码错误提示   截图已上传
  #43 [UAT] 用户登录 - S05 退出登录后跳转  ⚠ 无截图

/uat:run   修复后重新验证
```
