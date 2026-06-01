---
name: import
description: 导入 Swagger - 解析 OpenAPI 文档并展示接口概览
---

# 导入 Swagger

从配置的数据源解析 Swagger/OpenAPI 文档，展示接口概览。

## 命令格式

```
/api:import [--name=服务名] [--url=临时URL] [--file=临时文件]
```

## 参数说明

| 参数 | 说明 |
|------|------|
| `--name` | 仅导入指定名称的数据源（默认导入所有） |
| `--url` | 临时指定 URL，不修改配置文件 |
| `--file` | 临时指定本地文件，不修改配置文件 |

## 执行流程

### 前置检查

参考 `_common.md` 的「命令执行前置检查」。

### 解析流程

1. **读取数据源配置**
   - 有 `--url` 或 `--file` 参数 → 使用临时数据源
   - 无参数 → 从 `.api-config.json` 读取所有 sources
   - 有 `--name` → 过滤匹配的 source

2. **逐个解析数据源**

   对每个 source 调用 `swagger-parser.py`（`mode=summary`；URL 数据源用 `--url`，本地文件用 `--file`）。

3. **展示解析结果**

   ```
   导入 Swagger 文档

   === 主服务 (http://localhost:8080/swagger/doc.json) ===
   版本：OpenAPI 3.0.1
   标题：My API Server
   接口总数：42

   按 Tag 分组：
   
   Tag          数量 描述                        
   
   用户管理      8   用户注册、登录、信息管理      
   订单管理      12  订单创建、查询、状态流转      
   商品管理      10  商品 CRUD、分类、搜索        
   系统设置      6   权限、角色、配置管理          
   无分组        6   未归类接口                   
   

   ✅ 导入完成，使用 /api:search <关键词> 搜索接口
   ```

4. **解析失败处理**

   | 错误 | 提示 |
   |------|------|
   | URL 无法访问 | `❌ 无法访问 <url>，请检查后端服务是否启动` |
   | 文件不存在 | `❌ 文件 <path> 不存在` |
   | 格式错误 | `❌ 文件格式不是有效的 OpenAPI 文档` |
   | Python 未安装 | `❌ 需要 Python 3，请先安装：brew install python3` |

## 多数据源导入

配置了多个数据源时，逐个导入并汇总：

```
导入 Swagger 文档

=== 主服务 ===
接口总数：42 ✅

=== 支付服务 ===
接口总数：15 ✅

汇总：2 个数据源，57 个接口
```

## 注意事项

- 每次 import 都是实时解析，不做缓存
- 大型 Swagger 文档（>500 接口）时，Python 脚本仅输出摘要，具体接口按需查询
- 如果 Swagger 文档需要认证（如 Bearer Token），需在 URL 中携带或在配置中添加 headers（后续版本支持）
