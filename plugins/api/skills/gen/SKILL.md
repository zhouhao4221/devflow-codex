---
name: gen
description: |
  代码生成 - 根据接口定义生成 TypeScript 类型和请求函数
---

# 代码生成

根据 Swagger 接口定义，自动生成 TypeScript 类型定义和请求函数代码。

## 命令格式

```
/api:gen <METHOD> <path> [--name=服务名] [--type-only] [--request-only] [--tag=分组名]
```

## 参数说明

| 参数 | 必填 | 说明 |
|------|------|------|
| `METHOD` | 是 | HTTP 方法，或 `*` 表示该路径所有方法 |
| `path` | 是 | API 路径 |
| `--name` | 否 | 指定数据源 |
| `--type-only` | 否 | 仅生成类型定义 |
| `--request-only` | 否 | 仅生成请求函数 |
| `--tag` | 否 | 按 Tag 批量生成该分组下所有接口 |

## 执行流程

### 前置检查

1. 参考 `_common.md` 的「命令执行前置检查」
2. 执行请求库自动检测（参考 `_common.md`「请求库自动检测」）
3. 读取 `codegen.outputDir` 和 `codegen.typeDir`

### 生成流程

1. **解析接口定义**

   调用 `swagger-parser.py`（`mode=detail`，传入接口路径），获取接口完整 schema。

2. **检测请求库**

   按 `_common.md`「请求库自动检测」规则检测，确定代码风格。

3. **生成类型定义文件**

   目标路径：`{typeDir}/{模块名}.ts`

   模块名从 API 路径推断：
   - `/api/v1/users/{id}` → `user.ts`
   - `/api/v1/orders/{id}/items` → `order.ts`
   - 同一资源的接口类型合并到同一文件

   **文件已存在时**：
   - 读取现有文件，检查是否已有同名 interface
   - 未有 → 追加到文件末尾
   - 已有 → 进入**字段变更分析**（见步骤 3.1）

#### 3.1 字段变更分析（已有同名 interface 时）

将 Swagger 最新 schema 与项目中已有的 interface 逐字段比对：

```
检测到已有类型：UserDetailResponse

  字段变更：

  | 字段 | 变化 | 旧定义 | 新定义 |
  |------|------|--------|--------|
  | nickName | 新增 | — | string |
  | avatarUrl | 类型变更 | string | string \| null |
  | roleList[].permissions | 新增 | — | string[] |
  | phone | 删除 | string | — |

  无变化字段：id, userName, email, createdAt, isActive（省略）
```

**无字段变化时**：提示"类型定义无变化，跳过更新"，继续步骤 4。

**有字段变化时**：更新类型定义，并进入步骤 3.2 扫描关联页面。

#### 3.2 关联页面影响分析

AI 在项目中搜索引用了该类型或该请求函数的文件，识别受影响的页面组件：

在项目中搜索引用了该类型和请求函数的文件（`.ts`、`.tsx`、`.vue`）。对每个引用文件，AI 读取代码判断其用途：

| 用途 | 判断依据 | 影响 |
|------|---------|------|
| 表单页 | 包含 `<Form>`、`<Input>`、`onSubmit`、`formData` 等 | 新增字段需要加表单项，删除字段需要移除 |
| 列表/表格页 | 包含 `<Table>`、`columns`、`<List>` 等 | 新增字段可能需要加列，删除字段需要移除列 |
| 详情页 | 包含只读展示（`<Descriptions>`、`detail.xxx`） | 新增字段可能需要展示，删除字段需要移除 |
| 其他 | 仅 import 类型用于逻辑处理 | 需检查是否访问了已删除字段 |

输出影响分析报告：

```
关联页面影响分析：

  变更字段：+2 新增, 1 类型变更, 1 删除

  受影响文件（4个）：

  src/pages/user/UserForm.tsx（表单）
     - nickName（新增）→ 建议添加表单项
     - phone（删除）→ 需移除表单项和校验规则

  src/pages/user/UserList.tsx（列表）
     - nickName（新增）→ 可选：添加表格列
     - phone（删除）→ 需移除表格列定义

  src/pages/user/UserDetail.tsx（详情）
     - nickName（新增）→ 建议添加展示项
     - avatarUrl（类型变更）→ 需处理 null 值
     - phone（删除）→ 需移除展示项

  src/hooks/useUserPermission.ts（逻辑）
     - roleList[].permissions（新增）→ 无需改动（新字段）

是否自动生成调整方案？
```

#### 3.3 生成调整方案（用户确认后）

用户确认后，AI 对每个受影响文件给出具体的修改方案：

```
调整方案：

1/3 src/pages/user/UserForm.tsx 

  + 添加 nickName 表单项（在 email 字段后）：
    <Form.Item label="昵称" name="nickName">
      <Input placeholder="请输入昵称" />
    </Form.Item>

  - 移除 phone 表单项和校验规则

2/3 src/pages/user/UserList.tsx 

  - 移除 phone 列定义
  (nickName 为列表非关键字段，建议暂不添加)

3/3 src/pages/user/UserDetail.tsx 

  + 添加 nickName 展示项
  ~ avatarUrl 添加空值处理：{detail.avatarUrl ?? '—'}
  - 移除 phone 展示项

是否执行调整？（可选择部分文件执行）
```

用户可以：
- 全部执行 → AI 依次修改所有文件
- 选择部分执行 → 指定文件编号
- 仅更新类型 → 跳过页面调整，只更新 interface

4. **生成请求函数文件**

   目标路径：`{outputDir}/{模块名}.ts`

   同样合并同一资源到同一文件。
   **请求函数已存在时**：检查参数和返回类型是否变更，有变更则更新。

5. **展示生成结果**

### 输出格式

```
代码生成：GET /api/v1/users/{id}

检测请求库：axios（封装文件：src/utils/request.ts）

生成文件 

1. src/types/api/user.ts（类型定义）
2. src/api/user.ts（请求函数）

预览 

// src/types/api/user.ts

/** 用户详情 - 响应类型 */
export interface UserDetailResponse {
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
}

// src/api/user.ts

import request from '@/utils/request';
import type { UserDetailResponse } from '@/types/api/user';

/** 获取用户详情 */
export function getUserDetail(id: number) {
  return request.get<UserDetailResponse>(`/api/v1/users/${id}`);
}
```

确认后写入文件。

### 不同请求库的生成风格

#### 自定义封装（检测到 src/utils/request.ts 等）

```typescript
import request from '@/utils/request';

/** 获取用户列表 */
export function getUserList(params?: UserListParams) {
  return request.get<UserListResponse>('/api/v1/users', { params });
}

/** 创建用户 */
export function createUser(data: CreateUserParams) {
  return request.post<CreateUserResponse>('/api/v1/users', data);
}
```

#### axios（package.json 中有 axios）

```typescript
import axios from 'axios';

/** 获取用户列表 */
export function getUserList(params?: UserListParams) {
  return axios.get<UserListResponse>('/api/v1/users', { params });
}
```

#### umi-request

```typescript
import { request } from 'umi';

/** 获取用户列表 */
export function getUserList(params?: UserListParams) {
  return request<UserListResponse>('/api/v1/users', { method: 'GET', params });
}
```

#### 原生 fetch

```typescript
/** 获取用户列表 */
export async function getUserList(params?: UserListParams): Promise<UserListResponse> {
  const query = params ? '?' + new URLSearchParams(params as any).toString() : '';
  const res = await fetch(`/api/v1/users${query}`);
  if (!res.ok) throw new Error(`HTTP ${res.status}`);
  return res.json();
}
```

#### @tanstack/react-query

```typescript
import { useQuery, useMutation } from '@tanstack/react-query';

/** 获取用户详情 */
export function useUserDetail(id: number) {
  return useQuery({
    queryKey: ['user', id],
    queryFn: async () => {
      const res = await fetch(`/api/v1/users/${id}`);
      if (!res.ok) throw new Error(`HTTP ${res.status}`);
      return res.json() as Promise<UserDetailResponse>;
    },
  });
}

/** 创建用户 */
export function useCreateUser() {
  return useMutation({
    mutationFn: async (data: CreateUserParams) => {
      const res = await fetch('/api/v1/users', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(data),
      });
      if (!res.ok) throw new Error(`HTTP ${res.status}`);
      return res.json() as Promise<CreateUserResponse>;
    },
  });
}
```

#### swr

```typescript
import useSWR from 'swr';

const fetcher = (url: string) => fetch(url).then(res => res.json());

/** 获取用户详情 */
export function useUserDetail(id: number) {
  return useSWR<UserDetailResponse>(`/api/v1/users/${id}`, fetcher);
}
```

### 批量生成

#### 按 Tag 批量生成

```
/api:gen --tag=用户管理

→ 生成该 Tag 下所有接口的类型和请求函数
→ 合并到同一个模块文件
```

#### 按路径通配

```
/api:gen * /api/v1/users
/api:gen * /api/v1/users/{id}

→ 生成该路径下所有 HTTP 方法的代码
```

### 文件合并策略

同一模块（如 user）的多个接口生成到同一文件：

```
/api:gen * /api/v1/users
/api:gen * /api/v1/users/{id}

→ src/types/api/user.ts   包含 UserListResponse, UserDetailResponse, CreateUserParams 等
→ src/api/user.ts          包含 getUserList, getUserDetail, createUser 等
```

**合并规则：**
- 同名 interface 已存在 → 覆盖（确认后）
- 同名函数已存在 → 覆盖（确认后）
- 新增的 → 追加到文件末尾
- import 语句自动去重
