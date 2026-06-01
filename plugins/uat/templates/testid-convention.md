# data-testid 命名约定

UAT 自动化测试依赖 `data-testid` 选择器定位元素。请前端开发在关键交互元素上添加此属性。

## 命名格式

```
<功能域>-<元素类型>
```

## 元素类型后缀

| 后缀 | 适用元素 |
|------|---------|
| `-input` | 输入框、文本域 |
| `-button` | 按钮（含图标按钮） |
| `-select` | 下拉选择框 |
| `-table` | 数据表格容器 |
| `-modal` | 弹窗容器 |
| `-form` | 表单容器 |
| `-list` | 列表容器 |
| `-item` | 列表单项 |

## 示例

```html
<!-- 客户管理 -->
<input data-testid="customer-name-input" />
<input data-testid="customer-import-file-input" />
<button data-testid="customer-add-button">新增</button>
<button data-testid="customer-submit-button">保存</button>
<button data-testid="customer-import-button">导入</button>
<button data-testid="customer-import-confirm-button">开始导入</button>
<table data-testid="customer-table" />
<div data-testid="customer-detail-modal" />
```

## 注意事项

- 只加在**测试关键路径**上的元素，不需要全覆盖
- 同一页面的 testid 必须唯一
- 不要用 testid 做 CSS 样式钩子
