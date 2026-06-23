# llm-test-defense - Design Spec

> Human-readable design narrative — rationale, audience, style, color choices, content outline.
>
> Machine-readable execution contract: `spec_lock.md` (color / typography / icon / image short form). Executor re-reads `spec_lock.md` before every SVG page to resist context-compression drift.

## I. Project Information

| Item | Value |
| ---- | ----- |
| **Project Name** | llm-test-defense |
| **Canvas Format** | PPT 16:9 (1280×720) |
| **Page Count** | 11 |
| **Design Style** | instructional + soft-rounded |
| **Target Audience** | 课程答辩场景 — 老师和同学，学术环境 |
| **Use Case** | 5-8 分钟课程答辩 / 项目展示 |
| **Created Date** | 2026-06-23 |

---

## II. Canvas Specification

| Property | Value |
| -------- | ----- |
| **Format** | PPT 16:9 |
| **Dimensions** | 1280×720 |
| **viewBox** | `0 0 1280 720` |
| **Margins** | left/right 60px, top/bottom 50px |
| **Content Area** | 1160×620 |

---

## III. Visual Theme

### Theme Style

- **Mode**: instructional — 概念分解；步骤式；并行讲解
- **Visual style**: soft-rounded — 圆角卡片、柔和阴影、现代感
- **Theme**: Light theme
- **Tone**: tech, professional, modern, innovative

### Color Scheme

| Role | HEX | Purpose |
| ---- | --- | ------- |
| **Background** | `#FFFFFF` | 页面背景（浅色主题） |
| **Secondary bg** | `#F8FAFC` | 卡片背景、区域背景 |
| **Primary** | `#0EA5E9` | 标题装饰、关键章节、图标 |
| **Accent** | `#F59E0B` | 数据高亮、重点信息、链接 |
| **Secondary accent** | `#8B5CF6` | 次要强调、渐变过渡 |
| **Body text** | `#1E293B` | 正文 |
| **Secondary text** | `#64748B` | 说明文字、注释 |
| **Tertiary text** | `#94A3B8` | 补充信息、页脚 |
| **Border/divider** | `#E2E8F0` | 卡片边框、分割线 |
| **Success** | `#16A34A` | 正向指标（绿色系） |
| **Warning** | `#DC2626` | 问题标记（红色系） |

### Gradient Scheme

```xml
<!-- Title gradient -->
<linearGradient id="titleGradient" x1="0%" y1="0%" x2="100%" y2="100%">
  <stop offset="0%" stop-color="#0EA5E9"/>
  <stop offset="100%" stop-color="#8B5CF6"/>
</linearGradient>

<!-- Background decorative gradient -->
<radialGradient id="bgDecor" cx="80%" cy="20%" r="50%">
  <stop offset="0%" stop-color="#0EA5E9" stop-opacity="0.15"/>
  <stop offset="100%" stop-color="#0EA5E9" stop-opacity="0"/>
</radialGradient>
```

---

## IV. Typography System

### Font Plan

**Typography direction**: 现代 CJK 无衬线

| Role | Font Stack |
| ---- | ---------- |
| **Heading** | `"Microsoft YaHei", "PingFang SC", sans-serif` |
| **Body** | `"Microsoft YaHei", "PingFang SC", sans-serif` |
| **Code** | `Consolas, "Courier New", monospace` |
| **Body size** | 16px |
| **Heading size** | 32px (H1), 24px (H2), 20px (H3) |

---

## V. Layout System

### Page Structure

- **Title page**: Full-width title + subtitle + author info
- **Content pages**: Card-based layout with soft-rounded corners
- **Section pages**: Large title + brief description
- **Summary page**: Key takeaways in card grid

---

## VI. Icon System

- **Library**: tabler-outline
- **Style**: Outline, 1.5px stroke
- **Size**: 24px (inline), 48px (section headers)
- **Color**: Inherits from Primary (#0EA5E9)

---

## VII. Visualization

No data charts in this deck — focus on architecture diagrams and code flow.

---

## VIII. Image Resource List

| # | Filename | Acquire Via | Status | Type | Description |
|---|----------|-------------|--------|------|-------------|
| 1 | architecture.png | placeholder | Ready | Diagram | System architecture flow |
| 2 | day1-flow.png | placeholder | Ready | Diagram | Day1 test case generation flow |
| 3 | day2-flow.png | placeholder | Ready | Diagram | Day2 Selenium test flow |
| 4 | day3-ui.png | placeholder | Ready | Screenshot | Gradio UI mockup |
| 5 | day4-charts.png | placeholder | Ready | Screenshot | pyecharts dashboard |

---

## IX. Content Outline

### Page 1: 封面
- Title: 基于 LLM 协同辅助自动化测试的登录测试用例生成与分析系统
- Subtitle: 使用 DeepSeek API、Selenium、Gradio 与 pyecharts 构建自动化测试闭环
- Author info placeholder

### Page 2: 项目背景与问题
- 三个核心痛点：人工编写成本高、测试场景容易遗漏、测试结果缺少统一分析
- 配图：传统测试流程 vs 自动化测试流程对比

### Page 3: 项目目标
- 五个目标：自动生成用例、自动执行测试、自动收集结果、自动生成可视化、提供统一界面
- 配图：闭环流程图

### Page 4: 系统架构
- 技术栈：Python, DeepSeek API, Gradio, Selenium, pytest, pandas, pyecharts
- 配图：系统架构图

### Page 5: Day1 — LLM 生成测试用例
- 功能说明：调用 DeepSeek API 生成结构化测试用例
- 输出：Excel + Markdown
- 配图：Day1 流程图

### Page 6: Day2 — Selenium 自动化测试
- 测试内容：正常登录、用户名异常、密码异常、边界值、安全攻击
- 输出：test_results.json + 失败截图
- 配图：Day2 流程图

### Page 7: Day3 — Gradio 统一平台
- 功能：生成用例、执行测试、手动测试、打开可视化
- 配图：Gradio UI 截图

### Page 8: Day4 — pyecharts 可视化
- 四类图表：输入类型分布、平均耗时、验证结果、类别×输入类型
- 配图：Dashboard 截图

### Page 9: 项目亮点
- LLM 辅助测试设计
- 自动化测试闭环
- 教学演示友好
- 结果可追踪

### Page 10: 不足与改进
- 当前不足：教学模拟页面、模型稳定性、测试规模有限、未接入 CI
- 改进方向：接入真实接口、JSON Schema 约束、扩展模块、GitHub Actions

### Page 11: 总结
- 核心价值：LLM + 自动化测试 + 可视化
- 结束语

---

## X. Speaker Notes

Speaker notes will be generated in Step 6 (Executor Phase) based on the defense document content.

---

## XI. Technical Constraints

- All SVGs must use viewBox `0 0 1280 720`
- Colors must match the locked palette in spec_lock.md
- Fonts must end with PPT-safe fallbacks
- Icons must use tabler-outline library
- No AI images — placeholder/mockup style only
