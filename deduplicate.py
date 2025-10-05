#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Deduplicate papers table
Creates a new table 'papers_deduped' with duplicates removed
"""
import sqlite3
import pandas as pd
import sys

# Fix Windows console encoding
if sys.platform == 'win32':
    import io
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

DB_PATH = "covid_bibliometric_ucc.db"

def build_key(row):
    """Build deduplication key: DOI -> PMID -> Title"""
    for k in ("doi", "pmid"):
        if k in row.index and pd.notna(row[k]) and str(row[k]).strip():
            return str(row[k]).strip().lower()
    t = str(row.get("title", "")).strip().lower()
    return " ".join(t.split())

def main():
    conn = sqlite3.connect(DB_PATH)

    print("=== Deduplication Process ===")
    print(f"Reading from: {DB_PATH}")

    # Read all papers
    df = pd.read_sql_query("SELECT * FROM papers;", conn)
    print(f"Original records: {len(df)}")

    # Build dedup keys
    df['_key'] = df.apply(build_key, axis=1)

    # Show duplicates before
    dups_before = df.groupby('_key').size().reset_index(name='count')
    dups_before = dups_before[dups_before['count'] > 1]
    print(f"Duplicate keys found: {len(dups_before)}")

    if not dups_before.empty:
        print("\nDuplicates to be removed:")
        for _, row in dups_before.head(10).iterrows():
            key_preview = row['_key'][:60] + "..." if len(row['_key']) > 60 else row['_key']
            print(f"  {key_preview}: {int(row['count'])} copies")

    # Keep first occurrence of each key
    df_deduped = df.drop_duplicates(subset='_key', keep='first').drop(columns=['_key'])
    print(f"\nAfter deduplication: {len(df_deduped)} records")
    print(f"Removed: {len(df) - len(df_deduped)} duplicate records")

    # Create new table
    target_table = "papers_deduped"
    cur = conn.cursor()

    # Drop existing table if present
    cur.execute(f"DROP TABLE IF EXISTS {target_table};")

    # Create new table with same schema
    cur.execute(f"""
    CREATE TABLE {target_table} AS
    SELECT * FROM papers WHERE 1=0;
    """)

    # Insert deduplicated data
    print(f"\nWriting to table: {target_table}")
    df_deduped.to_sql(target_table, conn, if_exists='replace', index=False)

    # Create indexes
    print("Creating indexes...")
    try:
        cur.execute(f"CREATE UNIQUE INDEX IF NOT EXISTS idx_{target_table}_doi ON {target_table}(doi);")
        cur.execute(f"CREATE UNIQUE INDEX IF NOT EXISTS idx_{target_table}_pmid ON {target_table}(pmid);")
    except Exception as e:
        print(f"[WARN] Index creation: {e}")

    conn.commit()

    # Verify
    verify = pd.read_sql_query(f"SELECT COUNT(*) as count FROM {target_table};", conn)
    print(f"\n[OK] Verified: {verify['count'].iloc[0]} records in {target_table}")

    print("\n=== Next Steps ===")
    print(f"1. Review the deduplicated table: {target_table}")
    print(f"2. If satisfied, you can rename it:")
    print(f"   ALTER TABLE papers RENAME TO papers_backup;")
    print(f"   ALTER TABLE {target_table} RENAME TO papers;")

    conn.close()

if __name__ == "__main__":
    main()
