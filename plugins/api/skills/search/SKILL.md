---
name: search
description: |
  搜索接口 - 按关键词搜索 Swagger 中的 API 接口
---

# 搜索接口

从 Swagger 文档中按关键词搜索匹配的 API 接口。

## 命令格式

```
/api:search <关键词> [--name=服务名] [--tag=分组名] [--method=GET|POST|PUT|DELETE]
```

## 参数说明

| 参数 | 必填 | 说明 |
|------|------|------|
| `关键词` | 是 | 搜索关键词，匹配路径、描述、summary |
| `--name` | 否 | 指定数据源名称，默认搜索所有 |
| `--tag` | 否 | 按 Tag 分组过滤 |
| `--method` | 否 | 按 HTTP 方法过滤 |

## 执行流程

### 前置检查

参考 `_common.md` 的「命令执行前置检查」。

### 搜索流程

1. **读取数据源配置**

2. **调用 `swagger-parser.py`**（`mode=search`，传入关键词）搜索匹配接口。

3. **展示搜索结果**

   ```
   搜索「用户」

   找到 5 个匹配接口（主服务）：

   
   #  方法    路径                      描述            
   
   1  GET     /api/v1/users            获取用户列表     
   2  POST    /api/v1/users            创建用户         
   3  GET     /api/v1/users/{id}       获取用户详情     
   4  PUT     /api/v1/users/{id}       更新用户信息     
   5  DELETE  /api/v1/users/{id}       删除用户         
   

   使用 /api:map GET /api/v1/users/{id} 查看字段映射
   使用 /api:gen GET /api/v1/users/{id} 生成代码
   ```

4. **无结果时**

   ```
   搜索「xxx」

   未找到匹配接口。

   尝试：
   - 使用更短的关键词
   - /api:import 确认数据源已导入
   - /api:search --tag=用户管理 按分组浏览
   ```

### 搜索匹配规则

关键词同时匹配以下字段（任一匹配即返回）：
- API 路径（如 `/users` 匹配 `/api/v1/users`）
- summary / description（中英文模糊匹配）
- operationId
- Tag 名称

### 按 Tag 浏览

不传关键词时列出所有 Tag 供浏览：

```
/api:search --tag=用户管理

用户管理 — 8 个接口


#  方法    路径                      描述            

1  GET     /api/v1/users            获取用户列表     
......     ...                      ...             

```
