# Go 后端项目架构（CLAUDE.md 建议片段）

> 请将以下内容追加到项目的 CLAUDE.md 中，并根据实际情况调整。

## 项目架构

### 技术栈

- 语言：Go 1.22+
- Web 框架：Gin
- ORM：GORM
- 数据库：MySQL 8.0, Redis 7
- API 风格：RESTful + Swagger 注解
- 测试：go test + gomock

### 分层架构

按以下顺序开发，每层职责明确：

| 层 | 职责 | 目录 | 说明 |
|----|------|------|------|
| Model | 数据模型定义 | `internal/model/` | 结构体、表名、字段标签 |
| Store | 数据访问 | `internal/store/` | CRUD 操作，SQL 查询 |
| Biz | 业务逻辑 | `internal/biz/` | 校验、组合、事务 |
| Controller | 接口处理 | `internal/controller/v1/` | 参数绑定、响应封装 |
| Router | 路由注册 | `internal/router/` | 路由分组、中间件 |

### 文件命名

- Go 文件：kebab-case（如 `sys-dept-channel.go`）
- 测试文件：与源文件同目录 `*_test.go`

### 开发规范

- 错误处理：`errno.ErrXxx` 错误码，非裸 error
- 日志：`log.Info/Error(msg, ctx, k, v...)` 结构化日志，非 `fmt.Println`
- 多租户：所有业务表包含 `TenantID` 字段
- 权限标识：`module:resource:action` 格式
- Controller：Swagger 注解（Summary、Param、Success、Failure），`ShouldBindJSON`/`ShouldBindQuery` 参数绑定，`response.Success(c, data)`/`response.Error(c, err)` 响应

### 测试规范

- UT：与源文件同目录 `*_test.go`，gomock 模拟依赖
- API 测试：`tests/api/` 目录
- E2E 测试：`tests/e2e/`（如有前端）
- 测试环境：`docker-compose.test.yml`（MySQL + Redis 容器）
- 运行命令：`go test ./...`
