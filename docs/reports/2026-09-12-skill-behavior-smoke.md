# DevFlow skill 行为实测

日期：2026-09-12。结论：本轮三个行为场景全部通过，独立复跑完整回归为 11/11。

## 方式与范围

使用独立桌面端 Codex 子代理，直接读取当前工作区的 `plugins/req/skills/test-new/SKILL.md` 和 `fix/SKILL.md`，在两个隔离的 Python 标准库项目中执行真实任务。子代理只获得请求、skill 路径和项目文件，没有获得预期输出或具体修复代码。主会话用文件哈希、Git 状态、原测试方法 AST、独立测试执行和错误实现注入核对结果。

项目基线为 main 分支，5 项 unittest 中 3 项通过、2 项上边界用例失败；`normalize_tag` 没有测试。两个副本均无 remote，未提交或新增分支。原始测试项目保留不变。

本轮覆盖 skill 正文的执行行为；未测试 marketplace 安装、菜单发现、大 PR 审查及真实 GitHub/Gitea 评论。

## 结果

| 场景 | 实际结果 | 独立证据 |
|------|----------|----------|
| `test-new --files=src/tags.py --type=ut --dry-run` | 输出测试方案及拟创建内容，没有要求需求编号或落盘 | 项目文件哈希全部一致，git status 为空；子代理仅执行读取和状态检查 |
| `fix` 修复 clamp 上边界 | 将 `min(upper - 1, ...)` 修为 `min(upper, ...)`，执行编译及回归并报告 lint 未配置 | 仅修改 `src/limits.py`；原有 5 个测试方法 AST 完全一致；独立回归 5/5 |
| `test-new --files=src/tags.py --type=ut` | 新建 6 个 UT，覆盖大小写、混合空白、空字符串、纯空白、标点与 Unicode | 相对修复后快照仅新增 `tests/test_tags.py`，目标源码未变、未创建需求目录；新测试 6/6、完整回归 11/11 |

独立编译通过。两份副本 HEAD 均仍为基线 `1a484301d7fa5ed5b2220e2eb3d0ec78d6598f49`，只有 main 分支，无 remote。

## 新测试的有效性

在额外临时副本中替换 `normalize_tag` 实现，然后只运行新生成的 6 项测试；测试完成后删除这些错误实现副本。

| 故意引入的错误 | 结果 |
|----------------|------|
| 直接返回原字符串，完全不归一化 | 5 项失败，成功检出 |
| 保留空白归一化，但移除小写转换 | 4 项失败，成功检出 |
| 仅替换单个空格，不合并混合空白 | 3 项失败，成功检出 |

## 环境问题

最初尝试本机 `codex-cli 0.152.1` 的 `codex exec`；两个会话均在模型启动阶段返回 400，提示配置中的 `gpt-6-astra` 需要更新的 Codex 版本，尚未执行用户任务。随后改用桌面端独立子代理，未更换模型或修改 CLI 配置。

默认 Python 字节码缓存目录没有写权限，编译首次失败。子代理如实报告并改用临时可写缓存目录，编译通过后清理；主会话独立编译也通过。没有通过改测试断言或关闭检查来处理失败。

## 本机复查

实际执行后的项目：`/private/tmp/devflow-behavior-l6_htsmn/workflow`。

```bash
cd /private/tmp/devflow-behavior-l6_htsmn/workflow
python3 -B -m unittest tests.test_tags -v
python3 -B -m unittest discover -s tests -v
git diff -- src/limits.py
git status --short --branch
```

临时证据目录 `/private/tmp/devflow-behavior-l6_htsmn/` 保存 `before.json`、`dry-run.audit.json`、`fix.audit.json`、`before-test-new.json`、`test-new.audit.json` 和 `compile.audit.json`。其中包含文件哈希、实际 diff、测试输出、退出码及错误实现检出结果；CLI 启动失败日志另存为 `*.events.jsonl`。临时文件可能被系统清理，本报告保留关键结论和验证方式。
