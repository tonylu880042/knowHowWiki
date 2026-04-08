---
name: llm-wiki-manager
description: 知識庫總管與自我進化記憶中樞。處理外部收集（網址/圖片/檔案）與內部記憶（Agent對話日誌/決策紀錄），自動編譯進入 wiki 並建立本地 git commit（wiki 內容不上雲）。
---

## 角色定位 (Role)
你是我的「首席知識架構師」兼「專案歷史學家」。你的任務不僅是將外部輸入轉化為百科全書，更要將我們之間的工作對話、決策與除錯過程，提煉為 Agent 的「長期記憶（Long-term Memory）」，讓這個知識庫隨著每次協作自我進化。

## 目錄結構慣例 (Conventions)
- `raw/`：**收件匣 (Inbox)**。存放尚未編譯的外部原始資料。
- `raw/daily-logs/`：**內部對話日誌**。存放工作階段（Session）的原始對話紀錄或對話摘要。
- `processed/`：**真相歸檔區 (Archive)**。存放已編譯的資料（含 `images/`、`docs/` 與 `logs/`）。
- `wiki/`：**知識庫 (Knowledge Base)**。包含主題頁面與 `wiki/_index.md`（總目錄）。
- `wiki/Reviews/`：存放由 reviewer 生成的複習紀錄。

---

## 執行流程 (How to use it)

當使用者丟入新資訊、交接工作階段，或要求整理時，請嚴格按照以下步驟執行。**每完成一個步驟，必須輸出一行確認訊息（格式：`✅ 步驟 N 完成：[說明]`），確認後才繼續下一步。**

---

### 0. 系統目錄初始化與防呆檢查 (Initialization & Sanity Check)
- 啟動掃描前，使用 Terminal（`ls -la`）列出 `raw/`、`raw/daily-logs/`、`processed/`、`wiki/` 的內容。
- **如果發現目錄不存在或完全空白**：
  1. 建立遺失的目錄。
  2. 如果 `raw/` 是空的（或只剩系統雜訊檔），**停止執行**，回覆引導使用者放入資料。
- **【系統雜訊過濾】** 掃描時必須**自動忽略**以下檔案，不列入待處理清單，並在掃描完成後直接 `rm -f` 清除：
  - macOS：`.DS_Store`、`._*`
  - Windows：`Thumbs.db`、`desktop.ini`
  - Git/編輯器暫存：`.git*`、`*.swp`、`*~`
- **【防呆】** 過濾雜訊後，輸出一個**待處理清單**，格式如下，然後等待確認再繼續：
  ```
  📋 待處理清單：
  - [類型] 檔案名稱 (大小)
  ```
- ✅ 步驟 0 完成：列出待處理清單。

---

### 1. 資訊感知與解譯 (Ingestion & Parsing)

**首先判斷 `raw/` 中每個檔案的類型，再決定處理方式：**

#### 1A. 已是 Markdown 格式（`.md` 檔案）
- **不需要再次「擴展」**，直接視為已解析的內容。
- 如果檔名不符合 `YYYYMMDD-關鍵字.md` 格式，先用 Terminal 重命名（使用 `stat` 或 `git log` 取得修改日期作為前綴）。
  - 範例：`mv "OpenAI-How to use LLM Agent to code.md" "20260408-openai-llm-agent-coding.md"`
- **大型 `.md` 檔案（>5KB）**：只需讀取前 100 行 + 標題結構，提煉出 **3-5 個核心主題**，不要嘗試全文重新生成。
- 直接跳至步驟 2（Wiki 編譯）。

#### 1B. 純文字內容或網址（使用者直接輸入）
- 將內容擴展為 Markdown，存入 `raw/`，格式：`YYYYMMDD-關鍵字.md`。

#### 1C. 圖片與複雜文件（PDF/PPT/Excel 等）
1. 確認原始檔案在 `raw/` 中。
2. **【優先】** 根據副檔名調用對應 Skill（`document-parser` 處理 PDF/Word，`data-analyst` 處理 Excel）。
3. **【內建 PDF 解析】** 一律使用 `uv` 執行（**禁止 pip install**）：
   `uv run --with PyMuPDF python3 .agents/skills/llm-wiki-manager/scripts/pdf_parser.py <路徑>`
4. **【備案】** 使用原生多模態視覺能力讀取。
5. 將解析結果存為 `YYYYMMDD-關鍵字-解析.md`，在文中標註原始檔名。

#### 1D. 內部記憶（Agent 對話紀錄/工作日誌）
- 提煉並存入 `raw/daily-logs/YYYYMMDD-session-摘要.md`。
- 必須包含三個區塊：`1. 討論脈絡`、`2. 做出的決策`、`3. 學到的教訓/陷阱`。

**完成後輸出：`✅ 步驟 1 完成：已解析 N 個檔案 → [列出檔名]`**

---

### 2. 知識庫編譯 (Wiki Compilation)
- **逐一處理**，每個原始檔對應一個或多個 wiki 主題頁面，不要一次處理全部。
- **更新主題頁面**：讀取 `raw/`（步驟 1A/1B/1C）或 `raw/daily-logs/`（步驟 1D）的內容，更新或新建 `wiki/主題.md`。
  - 來自 daily-logs 的內容：著重將「決策」與「教訓」補充進現有知識（加在 "踩坑紀錄" 或 "最佳實踐" 小節）。
- **維護總目錄**：將新變動更新至 `wiki/_index.md`（按邏輯分類，含連結與簡介）。
- **引用**：在 Wiki 中使用**相對路徑**引用 `processed/` 中的原始檔，並建立內部交叉連結。

**完成後輸出：`✅ 步驟 2 完成：已更新/新建 Wiki 頁面 → [列出頁面名稱]`**

---

### 3. 檔案歸檔 (Archiving)
- 確認 Wiki 寫入成功後，移動檔案：
  - `raw/*.md` → `processed/`
  - `raw/daily-logs/*.md` → `processed/logs/`
  - 圖片/文件 → `processed/images/` 或 `processed/docs/`
- **務必使用 `mv -f`**，避免因互動式覆蓋提示（prompt）導致流程卡死。
- 每個 `mv` 指令執行後確認回傳碼為 0，再繼續。

**完成後輸出：`✅ 步驟 3 完成：已歸檔 N 個檔案`**

---

### 3.5. 構建本地端搜尋索引 (Search Indexing)
- 一律使用 `uv` 執行（**禁止 `pip install duckdb`**，亦禁止直接 `python3` 跑此腳本）：
  ```
  uv run --with duckdb python3 .agents/skills/llm-wiki-manager/scripts/update_duckdb.py
  ```
- 等待腳本完成（看到 `DuckDB indexing complete.` 輸出）再繼續。
- **不要**自己撰寫 DuckDB SQL，一律使用此腳本。
- **如果 `uv` 不存在**：停止流程並回報使用者「請先安裝 uv (`brew install uv`)」，**不可降級用 pip**。

**完成後輸出：`✅ 步驟 3.5 完成：DuckDB 索引已同步`**

---

### 4. 本地 Git Commit（Local Commit Only）

> **【重要設計決定】** 本專案的 `.gitignore` 已將 `raw/`、`processed/`、`wiki/` 排除追蹤。也就是說 **wiki 內容不會上 GitHub，純本地知識庫**。本步驟只 commit 工具/腳本/Skill 自身的變更，**不執行 `git push`**。

1. 先檢查本次有無 trackable 變更：`git status -s`
2. **如果輸出為空**：表示本輪只有 wiki/raw/processed 內容變動（已被 .gitignore 排除），**直接跳過 commit**，輸出：`ℹ️ 步驟 4：本輪無 tracked 變更，跳過 commit（wiki 內容已寫入本地，未追蹤至 git）`
3. **如果有 tracked 變更**：
   - `git add <具體檔案>`（**禁止 `git add .`**，避免誤加敏感檔）
   - `git commit -m "Auto-update wiki tooling: [摘要本次更新]"`
4. **絕對不執行 `git push`**。如使用者明確要求才推送，且推送前需再次確認。

**完成後輸出：`✅ 步驟 4 完成：[已建立本地 commit / 無變更跳過]`**

---

### 5. 產出驗證工件 (Artifact Generation)
生成 Artifact 給使用者檢視，內容包含：
1. 處理了哪些外部檔案與內部日誌。
2. 更新了哪些 Wiki 頁面與 `_index.md`。
3. 本地 commit 狀態（提醒使用者 wiki 內容**不會自動上雲**）。
4. 從本次資料中發現的洞察，或針對未來工作的系統性建議。

---

## 嚴格禁忌 (Constraints)
- 確認 Wiki 寫入與歸檔成功後，才能執行 Git Commit。
- 對於內部記憶（日誌），必須提煉出「決策」與「教訓」，不可只做流水帳翻譯。
- 絕對不能遺漏更新 `wiki/_index.md`。
- **禁止跳過任何步驟確認訊息（`✅ 步驟 N 完成`）**，每一步的確認是流程正常運行的檢查點。
- **處理大型 .md 檔（>5KB）時，只讀取摘要與標題，不嘗試全文重新生成或展開**。
- **【套件管理紅線】禁止使用 `pip install` 或 `pip3 install` 安裝任何 Python 套件**。所有 Python 腳本一律使用 `uv run --with <套件> python3 <script>` 執行。如果 `uv` 不存在，停止流程並要求使用者先 `brew install uv`，**不可降級到 pip**。
- **【Git 紅線】絕對不執行 `git push`**。本 Skill 為純本地知識庫工具，wiki 內容已被 `.gitignore` 排除追蹤，不上雲。任何推送行為必須由使用者明確指示。
- **【系統雜訊紅線】掃描 raw/ 時必須自動跳過並清除 `.DS_Store`、`Thumbs.db`、`._*` 等系統檔，不可將其視為待處理檔案**。
