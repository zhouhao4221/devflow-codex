---
name: run
description: 执行 UAT 测试 - 按流程文档逐场景验收
---

# 执行 UAT 测试

> **Audience:** QA

读取测试流程文档，调用 uat-executor skill 逐场景执行，输出报告。

> **运行环境要求**：操作方式为 `browser` 时，必须在 **Codex Chrome** 或 **Codex 桌面端** 中运行，否则无法调用浏览器工具。

## 命令格式

```
/uat:run [module]
```

- 省略模块名：列出所有 flow 文档，提示用户选择
- 指定模块名：直接执行对应 flow 文档

---

## 执行流程

### 0. 前置检查：skill 是否已安装

检查 `.agents/skills/uat-executor/SKILL.md` 是否存在：

- 存在 → 继续
- 不存在 → 终止并提示：

```
❌ uat-executor skill 未安装

当前环境需要 skill 文件才能执行测试。
请先在 Codex 中运行：/uat:init
```

### 1. 确定执行范围

- 有参数 → 查找 `docs/uat/flows/<module>.md`
- 无参数 → 列出所有 flow 文档，用户选择（支持"全部"）

若 flow 文件不存在：
```
❌ 未找到测试流程文档：docs/uat/flows/<module>.md
使用 /uat:new <module> 创建
```

### 2. 激活 uat-executor skill

读取 flow 文档后，按 `.agents/skills/uat-executor/SKILL.md` 的指导执行：

- 检查运行环境（browser 模式下确认浏览器工具可用）
- 逐场景执行并记录结果

### 3. 写入报告

执行完毕后：
1. 创建 `docs/uat/screenshots/` 目录（如不存在）
2. 将报告写入 `docs/uat/reports/YYYY-MM-DD-<module>.md`（含「发现记录」节，若有发现项）
3. 更新 flow 文档元信息的 `最后执行` 字段

### 4. 输出汇总

在终端展示执行汇总（格式见 uat-executor skill），并提示：

```
报告已保存：docs/uat/reports/YYYY-MM-DD-<module>.md

/uat:report          查看完整报告
/uat:bug             将失败项（代码 bug）上报为 issue
```

**注**：执行中发现流程文档描述有误时直接更新 `docs/uat/flows/<module>.md`，无需额外操作。
