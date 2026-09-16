import { defineConfig, devices } from '@playwright/test';

/**
 * Playwright 配置模板
 * 复制到项目 tests/e2e/ 目录并根据需要修改
 *
 * 参考文档: https://playwright.dev/docs/test-configuration
 */
export default defineConfig({
  // 测试目录
  testDir: '.',

  // 测试文件匹配模式
  testMatch: '**/*.spec.ts',

  // 完全并行运行测试
  fullyParallel: true,

  // CI 环境下禁止 test.only
  forbidOnly: !!process.env.CI,

  // 失败重试次数
  retries: process.env.CI ? 2 : 0,

  // 并行工作进程数
  workers: process.env.CI ? 1 : undefined,

  // 报告器配置
  reporter: [
    ['html', { outputFolder: 'playwright-report' }],
    ['list'],
  ],

  // 全局配置
  use: {
    // 基础 URL
    baseURL: process.env.FRONTEND_URL || 'http://localhost:3000',

    // 收集失败测试的 trace
    trace: 'on-first-retry',

    // 失败时截图
    screenshot: 'only-on-failure',

    // 失败时录制视频
    video: 'on-first-retry',

    // 超时设置
    actionTimeout: 10000,
    navigationTimeout: 30000,
  },

  // 全局超时
  timeout: 60000,

  // 预期超时
  expect: {
    timeout: 10000,
  },

  // 浏览器配置
  projects: [
    {
      name: 'chromium',
      use: { ...devices['Desktop Chrome'] },
    },
    // 可选：添加更多浏览器
    // {
    //   name: 'firefox',
    //   use: { ...devices['Desktop Firefox'] },
    // },
    // {
    //   name: 'webkit',
    //   use: { ...devices['Desktop Safari'] },
    // },
  ],

  // 本地开发时自动启动前端服务
  // 注意：测试环境脚本会预先启动服务，这里设置 reuseExistingServer: true
  webServer: {
    command: 'npm run dev',
    url: 'http://localhost:3000',
    reuseExistingServer: true,
    timeout: 120000,
  },
});
