---
name: api-field-mapper
description: API 字段映射助手。编辑前端 TypeScript/Vue 文件时自动关联 Swagger 接口定义，提示字段映射关系。
metadata:
  filePattern:
    - "src/**/*.ts"
    - "src/**/*.tsx"
    - "src/**/*.vue"
  bashPattern: []
  priority: 30
---

# API 字段映射助手

当编辑前端文件时，自动检测是否涉及 API 调用，并关联 Swagger 接口定义提供字段映射辅助。

## 触发条件

编辑以下类型文件时触发：
- `src/**/*.ts` — TypeScript 文件
- `src/**/*.tsx` — React 组件
- `src/**/*.vue` — Vue 组件

## 工作流程

### 1. 检测 API 调用

读取当前编辑的文件，检测是否包含 API 调用特征：

```
检测模式：
- import ... from '@/api/...'
- import ... from '@/services/...'
- request.get/post/put/delete(...)
- axios.get/post/put/delete(...)
- fetch('/api/...')
- useSWR('/api/...')
- useQuery(...'/api/...')
```

### 2. 提取接口路径

从检测到的 API 调用中提取路径：

```typescript
// 能识别的模式
request.get<UserDetail>('/api/v1/users/' + id)  → GET /api/v1/users/{id}
request.post('/api/v1/users', data)             → POST /api/v1/users
fetch(`/api/v1/orders/${orderId}`)              → GET /api/v1/orders/{id}
```

### 3. 关联 Swagger 定义

如果项目配置了 `.api-config.json`：

1. 调用 Python 脚本查询匹配的接口定义
2. 对比代码中使用的字段名与 Swagger 定义
3. 提示可能的问题

### 4. 辅助提示

当检测到以下情况时主动提示：

**字段名不匹配：**
```
💡 API 字段映射提示

文件中使用了 `username`，但接口 GET /api/v1/users/{id} 返回的是 `user_name`
建议使用映射后的字段名 `userName`（camelCase）

使用 /api:map GET /api/v1/users/{id} 查看完整映射
```

**缺少类型定义：**
```
💡 检测到 API 调用但未找到类型定义

接口：POST /api/v1/users
建议：/api:gen POST /api/v1/users 生成类型和请求函数
```

**字段过期（Swagger 中已删除）：**
```
⚠️ 字段可能已过期

代码中使用了 `user.nickName`，但当前 Swagger 定义中未找到该字段
请确认接口是否已更新：/api:map GET /api/v1/users/{id}
```

## 非侵入原则

- 仅在检测到明确的 API 调用时触发
- 不自动修改代码，只提供建议
- `.api-config.json` 不存在时静默跳过
- 不阻塞正常编辑操作
