# 📚 knowHowWiki

> 一套由 LLM 驅動的個人知識管理系統 —— 把碎片資訊自動煉成可檢索、可複習的結構化百科全書。

## 為什麼需要它？

我們每天都在吸收大量資訊：影片逐字稿、技術文章、靈光一閃的想法、會議筆記、截圖、PDF……但這些資訊往往散落各處，幾天後就被遺忘。

**knowHowWiki** 解決的問題是：

- ❌ 收集了資料，卻再也沒打開過
- ❌ 想找之前看到的某個概念，卻不記得在哪裡
- ❌ 學了皮毛，沒有系統化地深入某個領域

## 系統架構

```
knowHowWiki/
├── raw/                    # 📥 收件匣 — 丟入任何原始資料
├── processed/              # 📦 真相歸檔區 — 已處理的原始資料
│   ├── images/             #    歸檔圖片
│   └── docs/               #    歸檔文件 (PDF/PPT/Excel)
├── wiki/                   # 📖 知識庫 — 結構化的知識頁面
│   └── Reviews/            #    複習紀錄與測驗歷程
└── .agents/skills/         # 🤖 AI 技巧定義
    ├── llm-wiki-manager/   #    知識庫總管
    └── llm-wiki-reviewer/  #    知識庫複習助手
```

資料的生命週期是單向的：

```
原始資料 → raw/ → AI 編譯 → wiki/ → 歸檔至 processed/
                                  ↓
                           Reviews/ (複習)
```

## 🤖 核心：兩個 AI Skills

本系統的靈魂是兩個為 Agentic Coding 工具（如 Claude Code、Google Antigravity）設計的自訂技巧（Skills）。它們各自扮演不同角色，相互搭配構成完整的**知識攝取 → 結構化 → 複習**閉環。

---

### 🏗️ Skill 1：`llm-wiki-manager`（知識庫總管）

**角色**：首席知識架構師  
**觸發時機**：當你想儲存靈感、網址、圖片、或任何檔案時

#### 它做什麼？

1. **資訊感知與解譯（Ingestion）**  
   接受任何格式的輸入 —— 純文字、URL、圖片、PDF/PPT/Excel —— 並將其轉化為 Markdown 短文存入 `raw/`。
   - 純文字 / URL → 擴展成有背景脈絡的完整短文
   - 圖片 → 用多模態能力分析，生成文字解析
   - 複雜文件 → 自動調用其他 Skill 協作解譯

2. **知識庫編譯（Compilation）**  
   讀取 `raw/` 中的所有待處理檔案，萃取核心概念，更新或建立 `wiki/` 中的主題頁面。自動建立交叉連結與來源引用。

3. **檔案歸檔（Archiving）**  
   確認 Wiki 已更新後，將原始檔案從 `raw/` 移至 `processed/`（依類型分入子目錄）。

4. **矛盾偵測（Health Check）**  
   新資料與舊知識衝突時，自動標注 `[!WARNING] 知識衝突`，保留雙方觀點。

5. **驗證報告（Artifact）**  
   每次編譯完成後，輸出一份結構化報告：處理了什麼、更新了什麼、發現了哪些盲點。

#### 安全機制

- `processed/` 下的檔案一旦歸檔，**永不修改**
- 必須確認 Wiki 寫入成功後，才執行歸檔搬移
- 所有引用強制使用相對路徑與精確檔名

---

### 🎓 Skill 2：`llm-wiki-reviewer`（知識庫複習助手）

**角色**：專屬知識導師  
**觸發時機**：當你說「幫我複習」、「這週學了什麼」、「來個隨堂測驗」時

#### 它做什麼？

1. **檢索與掃描（Context Retrieval）**  
   掃描 `wiki/` 中近期更新或指定主題的頁面，深度理解核心概念。

2. **三種複習模式（Review Generation）**  

   | 模式 | 說明 | 適合場景 |
   |------|------|----------|
   | 📋 **精華摘要** | 長篇知識濃縮為 3-5 個 Key Takeaways | 快速回顧 |
   | 🧪 **費曼問答** | 3 個啟發性測驗題，考「概念關聯」而非「死背名詞」 | 深度理解 |
   | 🎙️ **語音導覽草稿** | Lex Fridman 風格的口語化講稿 | 通勤聆聽 |

3. **歷程存檔（Review Archive）**  
   每次複習的內容自動存入 `wiki/Reviews/`，建立可追溯的學習歷程。

#### 安全機制

- **完全唯讀**：除了 `wiki/Reviews/` 之外，不會修改知識庫中任何檔案
- **基於事實**：所有複習內容 100% 來自 Wiki 既有內容，不捏造、不過度延伸

---

## 使用範例

### 收集知識（Manager）

```
你：幫我記一下，今天看了一個影片講 Claude Code 的工作流
    它的核心技巧叫 Grill Me，還有一個叫 Ralph Loop 的 AFK 代理…

AI：（自動擴展、編譯、歸檔，生成報告）
```

### 複習知識（Reviewer）

```
你：幫我複習這週學到的東西

AI：（掃描本週 Wiki 更新 → 生成精華摘要 + 費曼問答）
    
    🧪 測驗題 1：Grill Me 為什麼不使用 ask_user_question 工具？
    請用「注意力機制」和「token 效率」兩個角度來回答。
```

## 技術定位

本專案不是一個應用程式，而是一套**為 AI 代理設計的操作手冊**。它利用現代 Agentic Coding 工具的 Skill 系統，讓 AI 自動遵循預定義的知識管理流程。

**相容的 AI 工具**：
- [Google Antigravity](https://github.com/google-deepmind) — 透過 `.agents/skills/` 目錄自動載入
- [Claude Code](https://claude.ai/code) — 透過 `.claude/` 或 `.agents/` 目錄載入
- 任何支援 Skill/Workflow 協定的 Agentic Coding 工具

## License

MIT
