---
name: report
description: 查看测试报告 - 展示最近一次执行结果
---

# 查看测试报告

> **Audience:** QA

读取并展示最近一次 `/uat:run` 生成的测试报告。

## 命令格式

```
/uat:report [module]
```

- 省略模块名：列出所有模块的最新报告供选择
- 指定模块名：直接展示该模块最新报告

---

## 执行流程

### 1. 找到报告文件

扫描 `docs/uat/reports/` 目录：
- 找到匹配模块名的所有报告文件（格式：`YYYY-MM-DD-<module>.md`）
- 取日期最新的一份

若无报告文件：
```
❌ 暂无测试报告

先执行 /uat:run <module> 生成报告
```

### 2. 展示报告

直接展示报告文件内容（Markdown 格式，含汇总表和失败详情）。

报告末尾追加操作提示：

```
/uat:bug   将失败项上报为 Gitea issue
/uat:run   重新执行测试
```
