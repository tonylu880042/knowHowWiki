# Ubiquitous Language — 通用語言

## 定義

源自 Eric Evans《Domain-Driven Design》的核心概念。在 AI 輔助開發中，**人類是領域專家，AI 是開發者**，兩者需要一份共享的術語詞彙表來精確溝通。

> 「後來我可以說 '實體化串聯有 bug'，AI 立刻知道我在講什麼。」

## 為什麼在 AI 時代更重要

| 問題場景 | 沒有 Ubiquitous Language | 有 Ubiquitous Language |
|----------|--------------------------|----------------------|
| 描述 bug | 「那個建立檔案的流程有問題」 | 「Materialization Cascade 有 bug」 |
| AI 搜尋碼庫 | 用錯關鍵字 → 找不到相關程式碼 | 用準確術語 → 直擊核心模組 |
| 多輪對話 | 語義漂移 → AI 漸漸搞混概念 | 詞義固定 → 跨 session 一致 |
| 命名函式 | `createOnDisk()` / `realize()` 混用 | `materializeGhost()` 統一 |

## 實作方式

在專案根目錄維護 `ubiquitous-language.md`，內容結構如下：

### 實體定義

```markdown
### Ghost Entity（幽靈實體）
存在於資料庫中但不存在於檔案系統的實體。
- Ghost Lesson：僅有 DB 紀錄的課程
- Ghost Section：僅有 DB 紀錄的章節
- Ghost Course：僅有名稱、無 file_path 的課程
```

### 動詞定義

```markdown
### Materialize（實體化）
將 Ghost Entity 轉變為 Real Entity —— 在檔案系統中建立對應的目錄/檔案。

### Materialization Cascade（實體化串聯）
在 Ghost Course 中實體化 Lesson 時觸發的連鎖反應：
  1. Modal 要求使用者指定 Course 的 file_path
  2. 實體化 Course（指向已存在的目錄）
  3. 實體化 Section（建立目錄）
  4. 實體化 Lesson（建立檔案）
```

### 規則與約束

```markdown
### 不可逆性
一旦 Course 被賦予 file_path，它永遠不會回到 Ghost 狀態。
即使所有 Real Lesson 都被刪除或轉為 Ghost，Course 仍然是 Real。

### file_path 指派
不負責建立 Git repo。只指向一個已存在的目錄。
```

### 禁用語（Aliases to Avoid）

```markdown
❌ "Create on disk" → ✅ "Materialize"
❌ "Realize"        → ✅ "Materialize"
❌ "Plan" / "Plan Lesson" → ✅ "Ghost Course" / "Ghost Lesson"（Plans 已棄用）
```

## 維護節奏

1. 每次 [Grill Me 環節](grill-me-skill.md) 結束後 **立即更新**
2. 由 AI 自動提議修改內容 → 人類審核 → `git commit`
3. 新術語出現時即時加入，不累積

## 相關概念

- [Grill Me](grill-me-skill.md) — 產出新術語的主要來源
- [PRD 到 Issues 管線](prd-to-issues-pipeline.md) — PRD 和 Issue 中強制使用統一術語
- [Claude Code 工程工作流](claude-code-workflow.md) — Ubiquitous Language 是工作流的第二步

---
> **來源**：[原始逐字稿](../processed/20260407 claude_code_dev.md)
