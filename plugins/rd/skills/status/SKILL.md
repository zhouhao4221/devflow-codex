---
name: status
description: 查看需求状态 - 详细状态和进度
---

# 查看需求状态

执行模型：按[命令模型路由](../../shared/_command-models.md)中 `rd:status` 的档位执行；已作为执行子代理时不再次路由。

查看需求的详细状态和进度信息。

## 命令格式

```
/rd:status [REQ-XXX|QUICK-XXX]
```

**说明**：编号可选，省略时自动选择最近活跃的需求。

---

## 执行流程

### 0. 自动识别需求

未指定编号时，按 [_storage.md](../../shared/_storage.md) 解析需求根目录，扫描 `active/` 的 REQ 和 QUICK 文档；唯一则选中，多个则列出供用户选择。不要从缓存或 `INDEX.md` 选择。

### 1. 解析存储路径

合并 `.devflow/settings.json` 与 `.devflow/settings.local.json`。primary 读取本仓 `requirementsDir`，readonly 直接读取 `requirementSource.path` 所指主仓自身的 `requirementsDir`；配置缺失时报告必要字段，不猜测缓存路径。

### 2. 查找需求文档

依次查需求根目录的 `active/<编号>-*.md` 与 `completed/<编号>-*.md`。仅以实际文件为准，未找到时提示 `/rd:req` 查看列表。

### 3. 解析需求文档

提取关键信息：
- 元信息
- 生命周期状态
- 功能清单进度
- 测试要点进度
- 文件改动清单
- 变更记录

### 4. 输出详细状态

```

需求状态：REQ-001 部门渠道关联


元信息
编号：REQ-001
状态：开发中
优先级：P1
创建日期：2026-01-07
负责人：-
数据来源：本地 (primary)
项目：my-saas-product

生命周期
[x] 草稿         2026-01-07
[x] 待评审       2026-01-07
[x] ✅ 评审通过      2026-01-07
[>] 开发中       2026-01-08 ← 当前
[ ] 测试中
[ ] 已完成

功能清单（4/6 完成）
[x] 部门渠道关联
[x] 渠道范围校验
[x] 获取可选渠道接口
[x] 订单数据过滤
[ ] Dashboard数据过滤      ← 进行中
[ ] 缓存机制

测试要点（0/8 完成）
[ ] 部门创建时关联渠道
[ ] 部门更新时修改渠道关联
[ ] 上级部门未设置渠道，下级可任意选择
[ ] 上级部门已设置渠道，下级必须设置且为子集
[ ] 选择超出范围的渠道报错
[ ] 订单列表按渠道正确过滤
[ ] Dashboard 数据按渠道正确过滤
[ ] 缓存正确失效

文件改动（8/12 完成）
已完成：
internal/sys/model/sys_dept_channel_model.go ✅
internal/sys/store/sys_dept_channel_store.go ✅
internal/sys/biz/dept_channel.go ✅
internal/sys/biz/sys_dept.go ✅
internal/sys/controller/v1/sys_dept.go ✅
pkg/api/core/v1/sys_dept.go ✅
internal/sys/router.go ✅
internal/oms/store/sales_order_store.go ✅

待处理：
internal/oms/biz/sales_order_biz.go
internal/dashboard/store/sales_dashboard_store.go
internal/dashboard/biz/sales_dashboard_biz.go
docs/swagger/docs.go

变更记录
2026-01-07 初始版本

评审记录
2026-01-07 张三 通过 - 方案合理，可以开发



可用操作：
# primary 角色显示完整操作
- 继续开发：/rd:dev REQ-001
- 编辑需求：/rd:edit REQ-001
- 进入测试：/rd:test REQ-001

# readonly 角色仅显示只读操作
# - 查看需求列表：/rd:req
# - 查看模块：/rd:modules
```

---

## 简洁模式

使用 `--brief` 参数输出简洁信息：

```
/rd:status REQ-001 --brief
```

输出：
```
REQ-001 部门渠道关联
状态：开发中 | 功能：4/6 | 测试：0/8
```

---

## 批量查看

查看所有活跃需求状态：

```
/rd:status --all
```

输出：
```
活跃需求状态一览

| 编号 | 标题 | 状态 | 功能进度 | 测试进度 |
|------|------|------|---------|---------|
| REQ-001 | 部门渠道关联 | 开发中 | 4/6 | 0/8 |
| REQ-002 | 用户积分系统 | 待评审 | - | - |
| REQ-003 | 订单导出优化 | 草稿 | - | - |
```

## 用户输入

$ARGUMENTS
