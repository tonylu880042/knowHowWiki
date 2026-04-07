# PRD 到 Issues 管線

## 定義

將 [Grill Me](grill-me-skill.md) 對話成果自動轉化為可執行開發任務的兩段式流水線：

```
Grill Me 對話 ──→ Write PRD ──→ PRD to Issues ──→ GitHub Issues ──→ Ralph Loop
```

## 第一段：撰寫 PRD

觸發指令：呼叫 `write PRD` 技巧。

### AI 的三步流程

1. **第二次 Explore**：用[子代理](explore-subagent.md)重新探索代碼庫（Grill Me 時已做過一次，但 PRD 寫作需要更聚焦在模組邊界）
2. **Sketching Major Modules**：列出所有受影響的模組及其介面變化
3. **生成 PRD 並推送為 GitHub Issue**

### 模組審查——最關鍵的步驟

> 「我不需要看模組內部。我只想知道它們怎麼變化。」

這是 `write PRD` 技巧的內建步驟：AI 列出受影響模組，開發者只需審查**介面設計**。

| 審查焦點 | 案例中的思考 |
|----------|-------------|
| 新方法 vs 改參數 | `materializeCourseAndLesson()` 新方法 ✅ vs 給 `materializeGhost()` 加參數 ❌（API 不乾淨） |
| 模組歸屬 | Schema 變更 → DB 層 / API 路由 → API 層 / 按鈕 → 前端模組 |
| 測試位置 | 「在已有 test harness 的地方寫測試」→ `course-e2e.test.ts` |
| 排除範圍 | Plans 棄用 → 不在這次 PRD 中 |

### 是否審查 PRD 內容？

> **不需要。** AI 非常擅長摘要。PRD 是 Grill Me 對話的直接產物，可以信任它的摘要品質。

## 第二段：拆解為 Issues

觸發指令：`PRD to issues`。

因為 PRD 剛寫完還在 context 中，AI 可以直接拆解，無需重新理解。

### 每個 Issue 的結構

- 連結到 parent PRD
- 明確的建造內容（what to build）
- 驗收標準（acceptance criteria）
- 阻擋關係（blocked by #N）
- 關聯的使用者故事

### Issue 粒度控制——「甜蜜點」

Issue 要匹配 [Ralph Loop](ralph-loop-afk-agent.md) 的工作節奏：

| 粒度 | 問題 | 行動 |
|------|------|------|
| 太小 | 「隱藏一個按鈕」→ 啟動整個 Agent 不值得 | **合併** |
| 太大 | 整個功能 → AI 容易失焦或 context 溢出 | **拆分** |
| 甜蜜點 | 觸及 UI + API + 邏輯的垂直切片 | ✅ |

案例：AI 最初拆成 6 個 Issue → 開發者認為太碎 → 合併成 **4 個**：
1. Ghost Course 建立（Schema + API + UI）
2. Ghost Course UI + Lesson 建立按鈕（合併自 #2 和 #3）
3. Direct Delete 動作
4. Materialization Cascade

### 是否審查 Issues 內容？

> **不需要。** 它只是在擴展 PRD 中已有的內容。但**粒度合併需要人工微調**。

## 相關概念

- [Grill Me](grill-me-skill.md) — 上游：產出 PRD 所需的對話紀錄
- [Ralph Loop](ralph-loop-afk-agent.md) — 下游：消化 Issues
- [Ubiquitous Language](ubiquitous-language.md) — PRD 和 Issue 中使用的統一術語
- [Claude Code 工程工作流](claude-code-workflow.md)

---
> **來源**：[原始逐字稿](../processed/20260407 claude_code_dev.md)
