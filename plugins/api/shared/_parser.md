# Swagger 解析脚本

从本文件的[Swagger 解析脚本](../scripts/swagger-parser.py)链接解析实际安装路径。每个数据源单独调用，URL 用 `--url`、本地文件用 `--file`，二选一。输出 JSON 到 stdout；错误时非零退出。

`mode=...` 表示脚本的 `--mode` 参数，必须显式传入。省略时默认 `summary`，可能得到格式正确但用途错误的结果。

| 用途 | 参数 |
|------|------|
| 概览 | `--mode summary` |
| 接口列表 | `--mode list [--tag TAG]` |
| 搜索 | `--mode search --keyword 关键词` |
| 详情 | `--mode detail --path "METHOD /path"` |

示例：`python3 <实际脚本路径> --file ./openapi.json --mode detail --path "GET /api/users/{id}"`。先解析相对脚本路径到真实安装位置，再执行；不要将字面占位符传给 shell。
