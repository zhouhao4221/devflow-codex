---
name: map
description: |
  字段映射 - 分析接口请求/响应字段并映射到前端类型
---

# 字段映射

解析指定 API 接口的请求参数和响应字段，展示后端到前端的完整字段映射关系。

## 命令格式

```
/api:map <METHOD> <path> [--name=服务名] [--case=camelCase|snake_case|original]
```

## 参数说明

| 参数 | 必填 | 说明 |
|------|------|------|
| `METHOD` | 是 | HTTP 方法：GET / POST / PUT / DELETE / PATCH |
| `path` | 是 | API 路径，如 `/api/v1/users/{id}` |
| `--name` | 否 | 指定数据源，默认搜索所有数据源 |
| `--case` | 否 | 覆盖配置的字段命名风格 |

## 执行流程

### 前置检查

参考 `_common.md` 的「命令执行前置检查」。

### 映射流程

1. **解析接口定义**

   调用 `swagger-parser.py`（`mode=detail`，传入接口路径），获取该接口的完整 schema（参数、请求体、响应体、$ref 解析后的结构）。

2. **AI 分析字段映射**

   读取 Python 脚本输出的 JSON，按 `_common.md` 中的「字段映射规则」和「类型映射」进行分析。

3. **展示映射结果**

   分三个部分展示：路径/查询参数、请求体、响应体。

### 输出格式

```
字段映射：GET /api/v1/users/{id}

描述：获取用户详情
Tag：用户管理

路径参数 

| 字段 | 类型 | 必填 | 前端字段名 | 说明 |
|------|------|------|-----------|------|
| id   | integer | ✅ | id | 用户ID |

查询参数 

（无）

响应字段映射 (200) 

| # | 后端字段 | 类型 | 必填 | 前端字段名 | 转换 | 说明 |
|---|---------|------|------|-----------|------|------|
| 1 | id | integer | ✅ | id | — | 用户ID |
| 2 | user_name | string | ✅ | userName | snake→camel | 用户名 |
| 3 | avatar_url | string | — | avatarUrl | snake→camel | 头像地址 |
| 4 | email | string | ✅ | email | — | 邮箱 |
| 5 | created_at | string(date-time) | ✅ | createdAt | snake→camel | 创建时间 |
| 6 | is_active | boolean | — | isActive | snake→camel | 是否激活 |
| 7 | role_list | array | — | roleList | snake→camel | 角色列表 |
| 7.1 | role_id | integer | ✅ | roleId | snake→camel | 角色ID |
| 7.2 | role_name | string | ✅ | roleName | snake→camel | 角色名 |
| 8 | department | object | — | department | — | 所属部门 |
| 8.1 | dept_id | integer | ✅ | deptId | snake→camel | 部门ID |
| 8.2 | dept_name | string | ✅ | deptName | snake→camel | 部门名 |

TypeScript 类型预览 

interface UserDetailResponse {
  id: number;
  userName: string;
  avatarUrl?: string;
  email: string;
  createdAt: string;
  isActive?: boolean;
  roleList?: {
    roleId: number;
    roleName: string;
  }[];
  department?: {
    deptId: number;
    deptName: string;
  };
}

使用 /api:gen GET /api/v1/users/{id} 生成完整代码
```

### POST/PUT 请求体映射

POST/PUT 等有请求体的接口，额外展示请求体映射：

```
请求体字段映射 (application/json) 

| # | 后端字段 | 类型 | 必填 | 前端字段名 | 转换 | 说明 |
|---|---------|------|------|-----------|------|------|
| 1 | user_name | string | ✅ | userName | snake→camel | 用户名 |
| 2 | email | string | ✅ | email | — | 邮箱 |
| 3 | password | string | ✅ | password | — | 密码 |
| 4 | role_ids | array[integer] | — | roleIds | snake→camel | 角色ID列表 |

TypeScript 类型预览 

interface CreateUserParams {
  userName: string;
  email: string;
  password: string;
  roleIds?: number[];
}
```

### 嵌套对象处理

- 嵌套对象使用 `` 缩进展示层级关系
- 编号使用点号分隔表示层级（如 `7.1`、`7.2`）
- TypeScript 类型中，嵌套对象复杂时提取为独立 interface

### 接口未找到

```
❌ 未找到接口：GET /api/v1/users/{id}

可能原因：
- 路径拼写有误
- 使用 /api:search 用户 查找正确路径
- 使用 /api:import 确认数据源已导入
```

## 批量映射

支持通配符批量映射同一路径下的所有方法：

```
/api:map * /api/v1/users/{id}

→ 展示 GET、PUT、DELETE /api/v1/users/{id} 的所有映射
```
