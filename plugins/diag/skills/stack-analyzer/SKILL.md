---
name: stack-analyzer
description: |
  生产报错堆栈识别助手。仅在执行 /diag:diagnose 命令期间触发。
  根据日志片段识别多语言栈的异常格式（Java / Node / Python / Go / Ruby / PHP 等），
  抽取异常类型、错误消息、堆栈帧（文件/行号/方法），为下一步本地代码关联提供结构化输入。
---

# 生产报错堆栈识别助手

## 触发条件

仅在执行 `/diag:diagnose` 命令并获取到日志片段后触发。

## 输入

- `log_snippet`：SSH 拉回的日志文本（tail + grep 后）
- `language_hint`（可选）：服务配置里的语言提示，值为 `java / node / python / go / ruby / php` 之一

## 输出（结构化）

```yaml
error_type: "java.lang.NullPointerException"      # 异常类 / 错误类型
message: "Cannot invoke ... because coupon is null"   # 核心消息
frames:
  - file: "OrderService.java"
    line: 142
    method: "com.example.order.OrderService.submit"
    qualified: "com.example.order.OrderService"
  - file: "OrderController.java"
    line: 87
    method: "com.example.order.OrderController.create"
    qualified: "com.example.order.OrderController"
evidence: "2026-04-20 02:31:05 [http-nio-8080-exec-3] ERROR ..."   # 原始行截取，便于对照
```

无法识别时输出：

```yaml
error_type: "unknown"
message: "<摘要>"
frames: []
note: "未识别堆栈格式，原始片段见 evidence"
evidence: "<原始日志截取>"
```

## 识别策略（按 language_hint 优先）

### Java (Spring / Tomcat 等)

格式特征：
```
java.lang.NullPointerException: Cannot invoke ...
    at com.example.Foo.bar(Foo.java:42) ~[app.jar:?]
    at com.example.Baz.qux(Baz.java:87) ~[app.jar:?]
Caused by: ...
```

抽取规则：
- 异常行：正则 `^\w+(?:\.\w+)*(?:Exception|Error)(?::.*)?$`
- 帧行：`at <qualified>.<method>\(<file>:<line>\)`
- 保留 `Caused by` 链

### Node.js (V8 trace)

格式特征：
```
TypeError: Cannot read property 'foo' of undefined
    at OrderService.submit (/app/src/services/order.js:142:15)
    at /app/src/routes/order.js:87:23
    at processTicksAndRejections (node:internal/process/task_queues:96:5)
```

抽取规则：
- 首行：`<ErrorType>: <message>`
- 帧：`at (?:<method> )?\((?<file>.+):(?<line>\d+):(?<col>\d+)\)` 或 `at (?<file>.+):(?<line>\d+):(?<col>\d+)`
- 内置模块（`node:internal/`）标注为"运行时内部"

### Python

格式特征：
```
Traceback (most recent call last):
  File "/app/order/service.py", line 142, in submit
    return self._calculate(coupon.discount)
AttributeError: 'NoneType' object has no attribute 'discount'
```

抽取规则：
- 帧：`File "<file>", line <line>, in <method>`
- 末行：`<ErrorType>: <message>`

### Go

格式特征：
```
panic: runtime error: invalid memory address or nil pointer dereference
[signal SIGSEGV: segmentation violation]

goroutine 42 [running]:
main.(*OrderService).Submit(0xc0001f0000, 0x0)
        /app/order/service.go:142 +0x2a
main.orderHandler(...)
        /app/order/handler.go:87
```

抽取规则：
- panic 首行 → error_type + message
- 帧：下一行是 `<file>:<line>`，上一行是 `<pkg>.<method>`

### Ruby

格式特征：
```
NoMethodError (undefined method `discount' for nil:NilClass):
  app/services/order_service.rb:142:in `submit'
  app/controllers/orders_controller.rb:87:in `create'
```

抽取规则：
- 首行：`<ErrorType> (<message>)`
- 帧：`<file>:<line>:in '<method>'`

### PHP

格式特征：
```
PHP Fatal error:  Uncaught TypeError: ... in /app/OrderService.php:142
Stack trace:
#0 /app/OrderController.php(87): OrderService->submit()
#1 {main}
```

抽取规则：
- 首行：`TypeError: <message>`
- 帧：`#<n> <file>(<line>): <class>-><method>\(\)`

### 未知 / 混合

若 `language_hint` 为空且首行不匹配上述特征：
- 尝试全部模式，取命中数最多的
- 仍无命中 → 输出 `error_type: "unknown"`，把日志中 `ERROR`/`Exception` 附近 20 行作为 evidence 返回

## 使用建议

- **不要构造堆栈**：识别不出就说"未识别"，不要猜测或编造帧。
- **保留原文**：`evidence` 字段必须是原始日志片段，便于人工核对。
- **优先 language_hint**：命中后不再尝试其他语言，减少误识别。
- **只抽取第一个异常链**：日志片段中可能有多个异常，只取最早/最完整的那个。
- **裁剪噪声**：框架内部帧（如 `org.springframework.web.*`、`node:internal/*`）放到 frames 末尾或标注，避免喧宾夺主。
