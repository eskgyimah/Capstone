#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Fix database schema and duplicates
- Add missing columns (source_database, citations_count)
- Show duplicate records
"""
import sqlite3
import pandas as pd
import sys

# Fix Windows console encoding
if sys.platform == 'win32':
    import io
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

DB_PATH = "covid_bibliometric_ucc.db"

def main():
    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()

    # 1. Check current schema
    print("=== Current Schema ===")
    schema = pd.read_sql_query("PRAGMA table_info(papers);", conn)
    print(schema[['name', 'type']].to_string(index=False))
    print()

    # 2. Add missing columns if needed
    existing_cols = schema['name'].tolist()

    if 'source_database' not in existing_cols:
        print("Adding 'source_database' column...")
        cur.execute("ALTER TABLE papers ADD COLUMN source_database TEXT;")
        conn.commit()
        print("[OK] Added source_database")
    else:
        print("[OK] source_database already exists")

    # Note: DB has 'citation_count' (singular) but app expects 'citations_count' (plural)
    if 'citation_count' in existing_cols and 'citations_count' not in existing_cols:
        print("[INFO] Found 'citation_count' (singular) - app expects 'citations_count' (plural)")
        print("      Consider updating Capstone.py to use 'citation_count' instead")
    elif 'citations_count' not in existing_cols:
        print("Adding 'citations_count' column...")
        cur.execute("ALTER TABLE papers ADD COLUMN citations_count INTEGER;")
        conn.commit()
        print("[OK] Added citations_count")
    else:
        print("[OK] citations_count already exists")

    print()

    # 3. Show duplicates
    print("=== Duplicate Analysis ===")
    df = pd.read_sql_query("SELECT * FROM papers;", conn)
    print(f"Total records: {len(df)}")

    # Build dedup keys
    def build_key(row):
        for k in ("doi", "pmid"):
            if k in row.index and pd.notna(row[k]) and str(row[k]).strip():
                return str(row[k]).strip().lower()
        t = str(row.get("title", "")).strip().lower()
        return " ".join(t.split())

    df['_key'] = df.apply(build_key, axis=1)
    dups = df.groupby('_key').size().reset_index(name='count')
    dups = dups[dups['count'] > 1].sort_values('count', ascending=False)

    print(f"Duplicate keys: {len(dups)}")
    if not dups.empty:
        print("\nTop duplicates:")
        for _, row in dups.head(10).iterrows():
            key_preview = row['_key'][:60] + "..." if len(row['_key']) > 60 else row['_key']
            print(f"  {key_preview}: {int(row['count'])} copies")

    print()
    print("=== Recommendations ===")
    print("1. Use 'Data Collection' → Deduplicate to create a clean table")
    print("2. Populate source_database and citations_count columns during data import")
    print("3. Check Orchestrator Dashboard → Duplicates tab for details")

    conn.close()

if __name__ == "__main__":
    main()
