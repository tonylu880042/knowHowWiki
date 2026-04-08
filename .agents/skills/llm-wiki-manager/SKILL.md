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

當使用者丟入新資訊、交接工作階段，或要求整理時，請嚴格按照以下步驟執行。

> **【執行模式紅線：一氣呵成】**
> 整個流程（步驟 0 → 5）必須在**單次回合**內連續執行完畢，**禁止在任何中間步驟停下來等待人類確認**。每完成一步，輸出一行 `✅ 步驟 N 完成：[說明]` 後**立即**開始下一步。
>
> 唯一允許停下的情況：步驟 0 發現 `raw/` 完全為空（沒有可處理的檔案）。
>
> 不要問「是否繼續？」、不要問「請確認」、不要產出 artifact 等使用者回應。使用者已經透過呼叫 skill 表達了「請執行整個流程」的意圖。

---

### 0. 系統目錄初始化與防呆檢查 (Initialization & Sanity Check)
- 使用單一 Terminal 指令完成所有掃描與清理（**一條 command line 解決，避免多次 round-trip**）：
  ```bash
  mkdir -p raw raw/daily-logs processed processed/logs processed/images processed/docs wiki wiki/Reviews && \
  find raw -maxdepth 2 \( -name '.DS_Store' -o -name '._*' -o -name 'Thumbs.db' -o -name 'desktop.ini' -o -name '*.swp' -o -name '*~' \) -delete && \
  ls -la raw/ raw/daily-logs/
  ```
- **如果掃描後 `raw/` 完全沒有可處理檔案**（只剩 `daily-logs/` 子目錄）：**停止執行整個流程**，回覆引導使用者放入資料。**這是唯一允許中止的情況**。
- 否則直接列出待處理清單並**立刻進入步驟 1，禁止等待使用者確認**：
  ```
  📋 待處理清單：
  - [類型] 檔案名稱 (大小)
  ```
- **完成後輸出**：`✅ 步驟 0 完成：發現 N 個待處理檔案，立即進入步驟 1`

---

### 1. 資訊感知與解譯 (Ingestion & Parsing)

**首先判斷 `raw/` 中每個檔案的類型，再決定處理方式：**

#### 1A. 已是 Markdown 格式（`.md` 檔案）
- **不需要再次「擴展」**，直接視為已解析的內容。
- **重命名規則（簡化版）**：如果檔名不符合 `YYYYMMDD-關鍵字.md` 格式，**直接使用「今天的日期」作為前綴**重命名。不要花時間用 `stat`、`git log`、`date -r` 之類的指令查歷史日期 — 排序前綴只需要可排序，不需要歷史精確。
  - 「今天的日期」從你的系統 context（`# currentDate`）取得，格式 `YYYYMMDD`。
  - **必須用雙引號包住含空格的舊檔名**：
    ```bash
    mv -f "raw/OpenAI-How to use LLM Agent to code.md" "raw/20260408-openai-llm-agent-coding.md"
    ```
  - 關鍵字命名：英數小寫 + hyphen，避免空格與特殊字元。
- **大型 `.md` 檔案（>5KB）讀取規則**：禁止讀取全文，**一律用 byte 為單位截斷**（不要用行數，避免單行超長字串的地雷）：
  ```bash
  head -c 5000 "raw/<檔名>.md" | fold -s -w 120
  ```
  - `head -c 5000`：取前 5000 bytes（約 2500 中文字或 5000 英文字），避免被「整個檔案只有一行」的字幕/逐字稿類檔案炸掉 context。
  - `fold -s -w 120`：強制換行成每行 120 字以內，方便閱讀。
  - 從這前 5KB 內容提煉 **3–5 個核心主題**，禁止嘗試重新生成或展開原文。
- 完成重命名後**直接跳至步驟 2**（Wiki 編譯），不要再讀第二次。

#### 1B. 純文字內容或網址（使用者直接輸入）
- 將內容擴展為 Markdown，存入 `raw/`，格式：`YYYYMMDD-關鍵字.md`。

#### 1C. 圖片與複雜文件（PDF/PPT/Excel 等）
1. 確認原始檔案在 `raw/` 中。
2. **【優先】** 根據副檔名調用對應 Skill（`document-parser` 處理 PDF/Word，`data-analyst` 處理 Excel）。
3. **【內建 PDF 解析】** 一律使用 `uv` 執行（**禁止 pip install**）：
   `uv run --with PyMuPDF python3 .agents/skills/llm-wiki-manager/scripts/pdf_parser.py <路徑>`
4. **【備案】** 使用原生多模態視覺能力讀取。
5. 將解析結果存為 `YYYYMMDD-關鍵字-解析.md`，在文中標註原始檔名。

#### 1D. 內部記憶（Agent 對話紀錄/工作日誌）— **嚴格 opt-in**

> **【觸發條件紅線】** 這個子步驟**預設不執行**。只有以下兩種情況才啟動：
> 1. 使用者在訊息中**明確**使用「記錄 session / 整理本次對話 / 做成 daily log / 提煉決策與教訓」等關鍵字（**要求產生新 session 檔案**）。
> 2. `raw/daily-logs/` 目錄中**已經存在**使用者預先放入的檔案，需要**提煉進 wiki**（**不是再生成一份 session 檔案**）。
>
> **【嚴禁腦補】** 不要因為「現在正在跟使用者對話」就自動把當前 conversation 歷史提煉成 daily log。若不確定，**直接跳過 1D**。

**兩種情境的處理規則（互斥）：**

**情境 A：使用者明確要求「記錄本次 session」**
- 輸出新檔案：`raw/daily-logs/YYYYMMDD-session-<關鍵字>.md`
- 必須包含三個區塊：`## 1. 討論脈絡`、`## 2. 做出的決策`、`## 3. 學到的教訓/陷阱`
- **【篇幅紅線】** 整份 ≤ 200 行 / ≤ 8KB。每區塊最多 5 個 bullet，每 bullet ≤ 2 行。禁止貼逐字稿、code diff、工具原始輸出。
- **【寫入方式紅線】** 先 Write 骨架（約 20 行含三個標題）**立刻送出**；再用 Edit 分段填入。禁止單次 Write 塞入 >200 行 content。

**情境 B：`raw/daily-logs/` 已有使用者預放檔案**
- **禁止**再建立新的 `YYYYMMDD-session-*.md` 檔案（**不要自創 digest**，該檔案本身就是原始輸入）。
- **【讀取紅線】** 對已存在的 daily-log 檔案，套用與 1A 相同的大型檔案規則：
  ```bash
  head -c 5000 "raw/daily-logs/<檔名>.md" | fold -s -w 120
  ```
  禁止讀取全文，禁止用 `head -n <行數>`（單行超長字幕檔會炸掉 context）。
- 從前 5KB 提煉 3–5 個核心主題，**直接跳至步驟 2**：在 wiki/ 建立或更新對應主題頁面（該檔案將於步驟 3 被歸檔至 `processed/logs/`）。

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
- **【一氣呵成紅線】整個流程必須在單次回合內連續執行完畢，禁止在中間步驟停下來問「是否繼續？」、「請確認」或產出 artifact 等使用者輸入**。唯一允許中止的狀況是步驟 0 發現 `raw/` 完全為空。
- **【重命名紅線】重命名 raw/ 中的檔案時，禁止使用 `stat`、`git log`、`date -r` 等指令查詢歷史日期**。一律使用 system context 中的「今天日期」當前綴。歷史精確不重要，可排序就好。
- **【大型檔案讀取紅線】處理 >5KB 的 .md 檔時，禁止用任何工具讀取全文**。一律使用 `head -c 5000 "<檔案>" | fold -s -w 120` 取前 5KB 再換行，禁止用 `head -n <行數>`（單行超長逐字稿/字幕檔會炸掉 context）。此規則同時適用於 `raw/` 與 `raw/daily-logs/`。
- **【Daily Log opt-in 紅線】步驟 1D（內部記憶/daily-logs）預設不執行**。除非使用者明確要求「記錄 session / 整理對話 / 做成 daily log」或 `raw/daily-logs/` 已有待處理檔案，否則**直接跳過**。禁止因為「正在跟使用者對話」就自動提煉當前 conversation。
- **【Write 篇幅紅線】任何單次 Write 工具呼叫的 content 參數，禁止超過 200 行或 8KB**。超過時必須改用「先 Write 骨架 → 再用 Edit 逐段填入」的分段寫法，避免 Write 卡在 `Creating +0 -0 🔄`。
