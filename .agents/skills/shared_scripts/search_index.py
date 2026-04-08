import duckdb
import argparse
import os

def search(db_path, keyword, limit=3):
    if not os.path.exists(db_path):
        print(f"錯誤：找不到資料庫 {db_path}，請先執行 upsert_index.py 建立索引。")
        return

    con = duckdb.connect(db_path, read_only=True)
    
    # 執行 FTS (Full Text Search) 檢索，使用 BM25 演算法計算相關度
    query = f"""
    SELECT 
        file_path, 
        title, 
        substring(content from 1 for 300) as snippet, 
        fts_main_wiki_docs.match_bm25(file_path, ?) AS score
    FROM wiki_docs
    WHERE fts_main_wiki_docs.match_bm25(file_path, ?) IS NOT NULL
    ORDER BY score DESC
    LIMIT ?
    """
    
    try:
        results = con.execute(query, (keyword, keyword, limit)).fetchall()
        
        if not results:
            print(f"找不到與「{keyword}」相關的文件。")
        else:
            print(f"關鍵字「{keyword}」的檢索結果：\n" + "="*50)
            for i, row in enumerate(results):
                file_path = row[0]
                title = row[1]
                # 簡單過濾掉換行符以美化輸出摘要
                snippet = row[2].replace('\n', ' ')
                score = row[3]
                
                print(f"[{i+1}] 檔案路徑: {file_path}")
                print(f"    文件標題: {title}")
                print(f"    相關度  : {score:.4f}")
                print(f"    內容摘要: {snippet}...")
                print("-" * 50)
                
    except duckdb.Error as e:
        print(f"搜尋失敗，可能尚未建立 FTS 索引或資料表異常。錯誤: {e}")
    finally:
        con.close()

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="在 DuckDB 中執行 FTS 前文檢索")
    parser.add_argument("keyword", help="要檢索的關鍵字")
    parser.add_argument("--db", default="processed/wiki_index.duckdb", help="DuckDB 資料庫路徑 (預設: processed/wiki_index.duckdb)")
    parser.add_argument("--limit", type=int, default=3, help="回傳的最大筆數 (預設: 3)")
    
    args = parser.parse_args()
    search(args.db, args.keyword, args.limit)
