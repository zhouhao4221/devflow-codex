---
name: test_regression
description: 回归测试 - 运行已有自动化测试用例
---

> **重要**：本命令的测试文件位置、运行命令、代码示例均从项目 CLAUDE.md 的「测试规范」章节读取，不内置任何项目细节。

# 回归测试

运行项目中已存在的自动化测试用例，验证功能正确性。

> 存储路径和缓存同步规则见 `_storage.md`

## 命令格式

```
/req:test_regression [选项]
```

### 选项

| 选项 | 说明 | 示例 |
|-----|------|------|
| `--all` | 全量回归（默认） | `/req:test_regression --all` |
| `--changed` | 仅测试变更相关 | `/req:test_regression --changed` |
| `--module=<name>` | 指定模块 | `/req:test_regression --module=user` |
| `--failed` | 仅运行上次失败的 | `/req:test_regression --failed` |
| `--type=<ut\|api\|e2e>` | 指定测试类型 | `/req:test_regression --type=ut` |
| `--verbose` | 显示详细输出 | `/req:test_regression --verbose` |
| `--coverage` | 生成覆盖率报告 | `/req:test_regression --coverage` |
| `--skip-env` | 跳过环境检查（仅 UT） | `/req:test_regression --type=ut --skip-env` |

---

## 测试环境要求

不同类型的测试需要不同的环境（具体服务和启动命令参考 CLAUDE.md）：

| 测试类型 | 依赖服务 | 后端服务 | 前端服务 |
|---------|---------|---------|---------|
| UT | 否 | 否 | 否 |
| API | 是 | 是 | 否 |
| E2E | 是 | 是 | 是 |

---

## 执行流程

### 0. 环境准备（API/E2E 需要）

如果测试类型包含 API 或 E2E，先检查并启动测试环境：

```
检查测试环境...

依赖服务状态：
<依赖服务 1>    ❌ 未启动
<依赖服务 2>    ❌ 未启动

按 CLAUDE.md 测试环境配置启动服务...
<CLAUDE.md中定义的测试环境启动命令>

等待服务就绪...
<依赖服务 1>  ✅ 就绪
<依赖服务 2>  ✅ 就绪

启动后端服务...
<CLAUDE.md中定义的后端启动命令>

等待后端服务...
<后端服务>  ✅ 就绪

启动前端服务（E2E 需要）...
<CLAUDE.md中定义的前端启动命令>

等待前端服务...
<前端服务>  ✅ 就绪

✅ 测试环境准备完成
```

### 1. 检测项目类型

从 CLAUDE.md 读取项目技术栈和测试框架配置：

```
检测项目类型...

项目类型：<CLAUDE.md中定义的技术栈>
测试框架：
单元测试：<CLAUDE.md中定义的UT框架>
API 测试：<CLAUDE.md中定义的API测试框架>
E2E 测试：<CLAUDE.md中定义的E2E框架>

测试目录：
<CLAUDE.md中定义的UT目录> (N 个文件)
<CLAUDE.md中定义的API测试目录> (N 个文件)
<CLAUDE.md中定义的E2E测试目录> (N 个文件)
```

### 2. 确定测试范围

根据选项确定要执行的测试：

#### 全量模式 (--all)
执行所有测试文件

#### 变更模式 (--changed)
```
检测变更文件...

变更文件：
<source-file-1>
<source-file-2>
<source-file-3>

关联测试：
<test-file-1>
<test-file-2>
<test-file-3>
```

#### 失败重试模式 (--failed)
从上次测试结果中读取失败用例

### 3. 执行测试

按类型依次执行：

```
执行回归测试...


单元测试 (<CLAUDE.md中的UT运行命令>)


<test-file-1>
<TestCase_1>           ✅ PASS
<TestCase_2>           ✅ PASS
<TestCase_3>           ✅ PASS
<TestCase_4>           ✅ PASS

<test-file-2>
<TestCase_5>           ✅ PASS
<TestCase_6>           ❌ FAIL
  Expected: <预期值>
  Actual:   <实际值>
<TestCase_7>           ✅ PASS

单元测试结果：N/N 通过


API 测试 (<CLAUDE.md中的API测试运行命令>)


<api-test-file-1>
<HTTP_METHOD> <endpoint-1>    ✅ PASS
<HTTP_METHOD> <endpoint-2>    ✅ PASS
<HTTP_METHOD> <endpoint-3>    ❌ FAIL
    Expected: 200
    Actual:   500 (Internal Server Error)

API 测试结果：N/N 通过
```

### 4. 生成测试报告

```

回归测试报告


测试时间：<timestamp>
测试范围：<全量回归 | 变更相关 | 失败重试>
总耗时：<duration>


类型     总数   通过   失败   通过率  

单元测试 N      N      N      XX.X%   
API 测试 N      N      N      XX.X%   
E2E 测试 N      N      N      XX.X%   

合计     N      N      N      XX.X%   


❌ 失败用例（N 个）：

1. <失败用例名>
   文件：<test-file>:<line>
   原因：<失败原因描述>

2. <失败用例名>
   文件：<test-file>:<line>
   原因：<失败原因描述>

下一步操作：
- 修复后重新测试：/req:test_regression --failed
- 查看失败详情：/req:test_regression --verbose
- 忽略失败继续：/req:test --force
```

### 5. 覆盖率报告（--coverage）

```
代码覆盖率报告


模块/目录                    覆盖率   状态     

<module-1>                  XX.X%    ✅ 达标   
<module-2>                  XX.X%    ⚠️ 接近   
<module-3>                  XX.X%    ❌ 不足   
<module-4>                  XX.X%    ✅ 达标   

总计                        XX.X%    <状态>    


目标覆盖率：<CLAUDE.md中定义的覆盖率目标>
建议补充测试：<覆盖率不足的模块>
```

---

## 测试框架配置

所有测试运行命令、目录结构、框架配置均从项目 CLAUDE.md 的「测试规范」章节读取，包括：

### 单元测试 (UT)

```bash
# 运行所有单元测试
<CLAUDE.md中的UT运行命令>

# 带覆盖率
<CLAUDE.md中的UT覆盖率命令>

# 指定模块
<CLAUDE.md中的UT运行命令> <module-path>

# 仅失败重试
<CLAUDE.md中的UT运行命令> <failed-test-filter>
```

### API 测试

```bash
# 前提：确保测试环境已启动（参考 CLAUDE.md 测试环境配置）

# 运行 API 测试
<CLAUDE.md中的API测试运行命令>

# 带详细输出
<CLAUDE.md中的API测试运行命令> --verbose

# 指定接口
<CLAUDE.md中的API测试运行命令> <test-filter>
```

### E2E 测试

```bash
# 前提：确保测试环境已启动（参考 CLAUDE.md 测试环境配置，包括前端服务）

# 运行所有 E2E 测试
<CLAUDE.md中的E2E运行命令>

# 带 UI 调试
<CLAUDE.md中的E2E运行命令> --ui

# 仅失败重试
<CLAUDE.md中的E2E运行命令> --last-failed

# 指定测试文件
<CLAUDE.md中的E2E运行命令> <test-file>
```

---

## 与 CI/CD 集成

回归测试结果可输出为 CI 友好格式：

```bash
/req:test_regression --ci --output=junit.xml
```

生成的报告可用于：
- GitHub Actions
- GitLab CI
- Jenkins

---

## 用户输入

$ARGUMENTS
