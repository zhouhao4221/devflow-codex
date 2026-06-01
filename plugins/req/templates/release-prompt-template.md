# Release 配置

> 本文件由 `/req:release` 在步骤 0 读取，注入项目特有的发版规则。
> 删除不需要的章节即可——所有章节均为可选，缺失时使用插件默认行为。

## 版本号文件

> 版本号确定后（步骤 2），自动更新并暂存以下文件中的版本号字段。
> 章节为空时跳过，不影响其他步骤。

<!--
示例：
- `package.json` → `version`（直接写入本次 release 版本号，去掉 v 前缀）
- `pyproject.toml` → `[project] version`
- `src/version.go` → `const Version = "<version>"`
-->

## 发版前检查

> 在生成任何产物（SQL 合并、changelog、commit）之前必须通过的检查。
> 检查失败时硬停止，不继续执行后续步骤。

<!--
示例：
- 运行测试：`npm test` / `go test ./...` / `pytest`
- 构建验证：`npm run build`
- Lint：`eslint src/`
-->

## 发版后步骤

> Release 创建成功后执行（草稿模式下不执行，publish 后由人工触发）。
> 仅输出提示，不自动执行副作用操作（通知、部署等由人工确认）。

<!--
示例：
- 通知渠道：发版后在 #releases 频道 @ 团队
- 部署：触发 staging 环境部署流水线
- 文档：更新 docs 站点版本号
-->

## 额外附件

> 除 SQL 文件外，需要上传到 Release 的其他文件或目录。
> 支持 glob 模式，路径相对项目根目录。

<!--
示例：
- `dist/app-*.zip`
- `docs/api-spec.yaml`
-->
