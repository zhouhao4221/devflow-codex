# 前端项目架构（CLAUDE.md 建议片段）

> 请将以下内容追加到项目的 CLAUDE.md 中，并根据实际情况调整。

## 项目架构

### 技术栈

- 框架：React 18+ / Next.js 16（根据实际选择）
- 语言：TypeScript
- 状态管理：Zustand / Redux Toolkit
- UI 组件：Ant Design / shadcn/ui
- 样式：Tailwind CSS / CSS Modules
- 构建：Vite / Turbopack
- 测试：Vitest + React Testing Library + Playwright

### 目录结构

| 目录 | 职责 | 说明 |
|------|------|------|
| `src/components/` | UI 组件 | 通用组件、业务组件 |
| `src/pages/` 或 `app/` | 页面/路由 | 文件系统路由或手动路由 |
| `src/hooks/` | 自定义 Hooks | 复用逻辑抽取 |
| `src/services/` 或 `src/api/` | API 调用 | 接口封装、类型定义 |
| `src/stores/` | 状态管理 | 全局状态 |
| `src/types/` | 类型定义 | 共享 TypeScript 类型 |
| `src/utils/` | 工具函数 | 通用工具 |

### 文件命名

- 组件文件：PascalCase（如 `UserProfile.tsx`）
- 工具/hooks：camelCase（如 `useAuth.ts`）
- 样式文件：与组件同名（如 `UserProfile.module.css`）

### 开发规范

- 组件：函数组件 + Hooks，避免 class 组件
- 类型：所有 props 和 API 响应定义 TypeScript 接口
- API 调用：统一封装 fetch/axios，集中管理接口地址
- 错误处理：ErrorBoundary + Toast 提示
- 国际化：i18next（如需）

### 测试规范

- 组件测试：`*.test.tsx`，React Testing Library
- 工具函数测试：`*.test.ts`，Vitest
- E2E 测试：`tests/e2e/`，Playwright
- 运行命令：`npm test` / `npx vitest` / `npx playwright test`
