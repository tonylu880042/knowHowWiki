import duckdb
import argparse
import os
from datetime import datetime

def init_db(db_path):
    # 確保資料庫存放目錄存在
    os.makedirs(os.path.dirname(db_path), exist_ok=True)
    con = duckdb.connect(db_path)
    
    # 建立文件資料表。
    # file_path 為 Primary Key。
    con.execute("""
        CREATE TABLE IF NOT EXISTS wiki_docs (
            file_path VARCHAR PRIMARY KEY,
            title VARCHAR,
            content VARCHAR,
            last_modified TIMESTAMP
        )
    """)
    return con

def upsert(db_path, target_file_path):
    if not os.path.exists(target_file_path):
        print(f"錯誤：找不到檔案 {target_file_path}")
        return

    # 讀取檔案內容
    with open(target_file_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # 將檔名（不含副檔名）作為預設標題
    title = os.path.basename(target_file_path).replace('.md', '')
    
    con = init_db(db_path)
    now = datetime.now()
    print(f"正在將 {target_file_path} 寫入資料庫...")
    
    # Upsert 資料
    con.execute("""
        INSERT INTO wiki_docs (file_path, title, content, last_modified)
        VALUES (?, ?, ?, ?)
        ON CONFLICT (file_path) DO UPDATE
        SET title = excluded.title,
            content = excluded.content,
            last_modified = excluded.last_modified
    """, (target_file_path, title, content, now))
    
    # DuckDB 的 FTS 索引需在資料變更後重新建立才能生效
    print("正在重建 FTS 索引...")
    try:
        con.execute("PRAGMA drop_fts_index('wiki_docs')")
    except duckdb.Error:
        # 如果是第一次執行，索引可能還不存在，忽略錯誤
        pass
        
    # 建立 FTS 索引。第一個參數是主鍵，後面是需要提供檢索的文字欄位。
    con.execute("PRAGMA create_fts_index('wiki_docs', 'file_path', 'title', 'content')")
    
    con.close()
    print("索引更新完成。")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="將 Markdown 檔案新增或更新至 DuckDB 的全文檢索索引")
    parser.add_argument("file_path", help="要處理的 Markdown 檔案路徑")
    parser.add_argument("--db", default="processed/wiki_index.duckdb", help="DuckDB 資料庫路徑 (預設: processed/wiki_index.duckdb)")
    
    args = parser.parse_args()
    upsert(args.db, args.file_path)
