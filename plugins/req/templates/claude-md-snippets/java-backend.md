# Java 后端项目架构（CLAUDE.md 建议片段）

> 请将以下内容追加到项目的 CLAUDE.md 中，并根据实际情况调整。

## 项目架构

### 技术栈

- 语言：Java 17+
- 框架：Spring Boot 3.x
- ORM：MyBatis-Plus / JPA
- 数据库：MySQL 8.0, Redis 7
- API 风格：RESTful
- 构建：Maven / Gradle
- 测试：JUnit 5 + Mockito

### 分层架构

按以下顺序开发，每层职责明确：

| 层 | 职责 | 目录 | 说明 |
|----|------|------|------|
| Entity | 数据模型 | `src/main/java/.../entity/` | 实体类、表映射 |
| Mapper/Repository | 数据访问 | `src/main/java/.../mapper/` | SQL 映射、CRUD |
| Service | 业务逻辑 | `src/main/java/.../service/` | 接口 + Impl 实现 |
| Controller | 接口处理 | `src/main/java/.../controller/` | 参数校验、响应封装 |

### 文件命名

- Java 文件：PascalCase（如 `SysDeptChannel.java`）
- 包名：小写（如 `com.example.system`）

### 开发规范

- 异常处理：自定义 BusinessException + 全局异常处理器
- 日志：`@Slf4j` + `log.info/error` 结构化日志
- 参数校验：`@Valid` + `@NotNull`/`@Size` 注解
- API 文档：SpringDoc / Swagger 注解
- 事务：`@Transactional` 注解

### 测试规范

- UT：`src/test/java/` 对应目录，Mockito 模拟依赖
- 集成测试：`@SpringBootTest` + `@TestContainers`
- API 测试：`MockMvc` 或 `RestAssured`
- 运行命令：`mvn test` / `gradle test`
