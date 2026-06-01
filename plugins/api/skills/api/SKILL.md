---
name: api
description: API 对接工具 - 列出接口概览和子命令帮助
---

# API 对接工具

前端 API 对接工具主入口，展示接口概览和可用命令。

## 命令格式

```
/api [--name=服务名] [--tag=分组名]
```

## 子命令

| 子命令 | 说明 | 示例 |
|-------|------|------|
| (空) | 列出接口概览 | `/api` |
| `config` | 配置管理 | `/api:config init` |
| `import` | 导入 Swagger | `/api:import` |
| `search` | 搜索接口 | `/api:search 用户` |
| `map` | 字段映射 | `/api:map GET /api/v1/users/{id}` |
| `gen` | 代码生成 | `/api:gen GET /api/v1/users/{id}` |

## 执行流程

### 无配置时

```
API 对接工具

⚠️ 尚未初始化配置

快速开始：
  1. /api:config init    — 初始化配置，添加 Swagger 数据源
  2. /api:import         — 导入并解析接口文档
  3. /api:search <关键词> — 搜索接口
  4. /api:map <接口>      — 查看字段映射
  5. /api:gen <接口>      — 生成类型和请求代码
```

### 有配置时

1. 读取 `.api-config.json`
2. 对每个数据源调用 `swagger-parser.py`（`mode=summary`）获取接口总数和分组概览。

3. 展示概览：

   ```
   API 对接工具

   数据源：
     1. 主服务 — http://localhost:8080/swagger/doc.json
        接口数：42  |  分组：用户管理(8) 订单管理(12) 商品管理(10) 系统设置(6) 其他(6)

     2. 支付服务 — ./docs/payment-swagger.json
        接口数：15  |  分组：支付(8) 退款(4) 对账(3)

   常用命令：
     /api:search <关键词>              搜索接口
     /api:map <METHOD> <path>         查看字段映射
     /api:gen <METHOD> <path>         生成代码
     /api:gen --tag=<分组名>           批量生成某分组代码
     /api:config                      查看/修改配置
   ```

### 按 Tag 过滤

```
/api --tag=用户管理

用户管理 — 8 个接口


#  方法    路径                      描述            

1  GET     /api/v1/users            获取用户列表     
2  POST    /api/v1/users            创建用户         
3  GET     /api/v1/users/{id}       获取用户详情     
4  PUT     /api/v1/users/{id}       更新用户信息     
5  DELETE  /api/v1/users/{id}       删除用户         
6  POST    /api/v1/users/{id}/reset 重置密码         
7  GET     /api/v1/users/export     导出用户数据     
8  POST    /api/v1/users/import     导入用户数据     

```

### 数据源连接失败

对无法访问的数据源标记状态：

```
数据源：
  1. 主服务 — http://localhost:8080/swagger/doc.json
     ❌ 无法访问，请检查后端服务是否启动

  2. 支付服务 — ./docs/payment-swagger.json
     接口数：15  |  分组：支付(8) 退款(4) 对账(3)
```
