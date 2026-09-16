# API 对接插件 - 使用教程

🌐 [English](tutorial.en.md) | [中文](tutorial.zh.md) | [한국어](tutorial.ko.md)

## 章节

 1. 快速开始
 2. 配置管理
 3. 导入 Swagger
 4. 搜索接口
 5. 字段映射
 6. 代码生成
 7. 自动检测
 8. 常见问题

---

## 1. 快速开始

三步上手：

### 第一步：初始化配置

在前端项目根目录执行：

```
/api:config init
```

按提示填写后端 Swagger 文档地址，生成 `.api-config.json`。

### 第二步：导入接口

```
/api:import
```

解析 Swagger 文档，展示接口概览和分组信息。

### 第三步：开发使用

```
/api:search 用户                       # 搜索接口
/api:map GET /api/v1/users/{id}        # 查看字段映射
/api:gen GET /api/v1/users/{id}        # 生成类型 + 请求函数
```

完整流程：

```
/api:config init → /api:import → /api:search → /api:map → /api:gen
初始化配置        导入文档       搜索接口       字段映射     生成代码
```

---

## 2. 配置管理

配置文件：项目根目录 `.api-config.json`

### 初始化

```
/api:config init
```

交互式生成配置，自动检测项目的 `src/api/`、`src/types/` 目录。

### 查看配置

```
/api:config
```

展示当前数据源、代码生成目录、检测到的请求库。

### 添加数据源

```
/api:config add
```

支持 URL（后端在线文档）和本地文件两种方式。

### 删除数据源

```
/api:config remove 支付服务
```

### 配置示例

```json
{
  "swagger": {
    "sources": [
      { "name": "主服务", "url": "http://localhost:8080/swagger/doc.json", "prefix": "/api/v1" },
      { "name": "支付服务", "file": "./docs/payment-swagger.json", "prefix": "/pay/v1" }
    ]
  },
  "codegen": {
    "outputDir": "src/api",
    "typeDir": "src/types/api",
    "fieldCase": "camelCase"
  }
}
```

建议将 `.api-config.json` 加入版本控制，团队共享配置。

---

## 3. 导入 Swagger

### 导入所有数据源

```
/api:import
```

### 导入指定数据源

```
/api:import --name=主服务
```

### 临时导入（不修改配置）

```
/api:import --url=http://other-service:8080/swagger/doc.json
```

### 支持格式

- OpenAPI 2.0（Swagger）
- OpenAPI 3.0.x / 3.1.x
- JSON 和 YAML 格式

依赖 Python 3，首次使用需确认已安装。

---

## 4. 搜索接口

### 关键词搜索

```
/api:search 用户
```

匹配接口路径、描述、Tag 名称，支持中英文。

### 按 Tag 浏览

```
/api:search --tag=用户管理
```

### 按方法过滤

```
/api:search 用户 --method=GET
```

### 指定数据源

```
/api:search 支付 --name=支付服务
```

### 搜索结果示例

```
🔍 搜索「用户」— 找到 5 个接口

┌────┬─────────┬──────────────────────┬──────────────┐
│ #  │ 方法    │ 路径                  │ 描述         │
├────┼─────────┼──────────────────────┼──────────────┤
│ 1  │ GET     │ /api/v1/users        │ 获取用户列表  │
│ 2  │ POST    │ /api/v1/users        │ 创建用户      │
│ 3  │ GET     │ /api/v1/users/{id}   │ 获取用户详情  │
└────┴─────────┴──────────────────────┴──────────────┘
```

---

## 5. 字段映射

核心功能：展示后端接口字段到前端的完整映射关系。

### 基本用法

```
/api:map GET /api/v1/users/{id}
```

### 输出内容

- 路径参数 / 查询参数
- 请求体字段映射（POST/PUT）
- 响应体字段映射
- TypeScript 类型预览

### 映射规则

```
后端 snake_case  →  前端 camelCase
user_name        →  userName
avatar_url       →  avatarUrl
created_at       →  createdAt
is_active        →  isActive
```

### 嵌套对象

嵌套字段用层级编号展示（如 7.1、7.2），TypeScript 中生成嵌套类型。

### 批量映射

```
/api:map * /api/v1/users/{id}
```

展示该路径下所有 HTTP 方法的映射。

---

## 6. 代码生成

根据接口定义生成 TypeScript 类型和请求函数。

### 基本用法

```
/api:gen GET /api/v1/users/{id}
```

生成两个文件：
- `src/types/api/user.ts` — 类型定义
- `src/api/user.ts` — 请求函数

### 仅生成类型

```
/api:gen GET /api/v1/users/{id} --type-only
```

### 仅生成请求函数

```
/api:gen GET /api/v1/users/{id} --request-only
```

### 批量生成

```
/api:gen --tag=用户管理          # 按 Tag 批量
/api:gen * /api/v1/users         # 该路径所有方法
/api:gen * /api/v1/users/{id}    # 该路径所有方法
```

### 请求库适配

插件自动检测项目使用的请求库，生成对应风格代码：
- 自定义封装文件（如 `src/utils/request.ts`）— 直接导入使用
- axios — `axios.get/post` 风格
- umi-request — `request()` 风格
- `@tanstack/react-query` — `useQuery/useMutation` hooks
- swr — `useSWR` hooks
- 原生 fetch — async/await 风格

---

## 7. 自动检测

### 请求库检测

代码生成时自动检测，无需配置。检测顺序：

1. 项目中的 request 封装文件（最高优先）
   - `src/utils/request.ts`
   - `src/lib/request.ts`
   - `src/services/request.ts`

2. `package.json` 中的依赖
   - axios / umi-request / `@tanstack/react-query` / swr / ky

3. 都未找到 → 使用原生 fetch

### Skill 自动关联

编辑前端 TypeScript/Vue 文件时，插件自动检测 API 调用，提示字段映射关系和可能的不匹配。

触发条件：编辑 `src/**/*.ts`、`src/**/*.tsx`、`src/**/*.vue`

---

## 8. 常见问题

### Python 未安装

```
❌ 需要 Python 3

解决：brew install python3（macOS）或 apt install python3（Linux）
```

### Swagger 地址无法访问

```
❌ 无法访问 http://localhost:8080/swagger/doc.json

检查：
- 后端服务是否已启动
- URL 是否正确（浏览器打开验证）
- 是否需要 VPN / 代理
```

### YAML 格式文档解析失败

```
❌ YAML 格式需要安装 pyyaml

解决：pip3 install pyyaml
```

### 生成的代码字段风格不对

修改 `.api-config.json` 中的 `fieldCase`：
- `"camelCase"` — 驼峰（默认）
- `"snake_case"` — 下划线
- `"original"` — 保持原样

### 多个后端服务

在 `.api-config.json` 的 `sources` 数组中添加多个数据源，每个指定不同的 `name` 和 `prefix`，搜索时用 `--name` 过滤。
