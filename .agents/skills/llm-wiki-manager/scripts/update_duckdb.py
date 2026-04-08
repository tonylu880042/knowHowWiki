import duckdb
import os
import sys
from datetime import datetime

DB_PATH = 'processed/wiki_index.duckdb'
WIKI_DIR = 'wiki'

def init_db():
    con = duckdb.connect(DB_PATH)
    # Create the table if it's missing just in case
    con.execute('''
        CREATE TABLE IF NOT EXISTS wiki_docs (
            file_path VARCHAR PRIMARY KEY,
            title VARCHAR,
            content VARCHAR,
            last_modified TIMESTAMP
        )
    ''')
    return con

def extract_title(content, filename):
    lines = content.split('\n')
    for line in lines:
        if line.startswith('# '):
            return line[2:].strip()
    return filename

def update_duckdb():
    con = init_db()
    
    # Process all markdown files in wiki/
    for root, dirs, files in os.walk(WIKI_DIR):
        for file in files:
            if file.endswith('.md'):
                file_path = os.path.join(root, file)
                try:
                    with open(file_path, 'r', encoding='utf-8') as f:
                        content = f.read()
                    
                    title = extract_title(content, file)
                    last_modified = datetime.fromtimestamp(os.path.getmtime(file_path))
                    
                    # Upsert (Insert or Replace) into DuckDB
                    # First delete existing entry
                    con.execute('DELETE FROM wiki_docs WHERE file_path = ?', (file_path,))
                    # Insert new entry
                    con.execute(
                        'INSERT INTO wiki_docs (file_path, title, content, last_modified) VALUES (?, ?, ?, ?)',
                        (file_path, title, content, last_modified)
                    )
                    print(f"Index updated for: {file_path}")
                except Exception as e:
                    print(f"Error processing {file_path}: {e}")

    con.close()
    print("DuckDB indexing complete.")

if __name__ == "__main__":
    update_duckdb()
