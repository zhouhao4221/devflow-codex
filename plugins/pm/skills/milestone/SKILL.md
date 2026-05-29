---
name: milestone
description: |
  里程碑总结 - 版本发布总结报告
---

# 里程碑总结

> **Audience:** Product Manager

基于 Git Tag 和需求完成记录，生成版本发布总结报告。

## 命令格式

```
/pm:milestone <版本号> [--from=<tag|commit>] [--save]
```

**参数说明：**
- `<版本号>`：**必填**，版本号（如 v1.6.0）
- `--from`：可选，起始点，默认上一个 Tag
- `--save`：可选，直接保存不询问

**示例：**
- `/pm:milestone v1.6.0` — 从上个 Tag 到当前
- `/pm:milestone v1.6.0 --from=v1.5.0` — 指定起始版本

---

## 执行流程

### 1. 确定版本范围

```bash
TO_REF=${version}  # 如果 tag 存在则用 tag，否则用 HEAD
FROM_REF=${from:-$(git describe --tags --abbrev=0 $TO_REF^ 2>/dev/null)}
```

### 2. 采集数据

- 范围内的 Git 提交和变更统计
- 从提交消息中提取关联需求编号
- 读取对应需求文档获取详细信息
- 计算版本开发周期（起止时间）

### 3. 输出里程碑报告

```

里程碑总结：<version>

项目：<project>
版本范围：<from-ref> → <to-ref>
开发周期：YYYY-MM-DD ~ YYYY-MM-DD（X 天）


## 版本概览

本版本聚焦于 XX 功能，包含 X 个需求交付、XX 个提交。
核心亮点：...（AI 从需求标题和提交类型推导）

## 交付需求

| 编号 | 标题 | 类型 | 交付功能点 |
|------|------|------|----------|
| REQ-005 | 用户积分兑换 | 后端 | 兑换规则、记录查询、限额校验 |
| QUICK-003 | 修复登录超时 | 全栈 | token 刷新竞态修复 |

## 代码统计

| 指标 | 数值 |
|------|------|
| 总提交 | XX |
| 代码变更 | +X,XXX / -XXX 行 |
| 变更文件 | XX 个 |
| 贡献者 | X 人 |

  提交类型：
  feat  XX 
  fix   XX 
  other XX 

## 贡献者

| 贡献者 | 提交数 | 占比 |
|--------|--------|------|
| 张三 | XX | XX% |
| 李四 | XX | XX% |


*由 /pm:milestone 自动生成 · YYYY-MM-DD*
```

### 4. 提供保存选项

```python
offer_save(content, f"docs/reports/milestone/{version}.md")
```

## 用户输入

$ARGUMENTS
