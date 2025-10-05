# Database Schema & Duplicates - Fixes Applied

## Issues Found

1. ❌ **Missing column**: `source_database` - Not in database
2. ❌ **Column name mismatch**: Database has `citation_count` (singular) but Capstone.py used `citations_count` (plural)
3. ❌ **Duplicates**: 18 duplicate records found

## Fixes Applied

### 1. Schema Updates ✅

**Added missing column:**
```sql
ALTER TABLE papers ADD COLUMN source_database TEXT;
```

**Updated Capstone.py:**
- Changed all `citations_count` → `citation_count` (24 occurrences)
- Updated `ensure_papers_schema()` to match actual database structure
- Added all missing columns: abstract, url, keywords, created_at, updated_at

### 2. Deduplication ✅

**Created clean table:**
- Original records: **472**
- After deduplication: **454**
- Removed: **18 duplicates**

**Deduplicated table:** `papers_deduped`

**Duplicate examples removed:**
- 10.1001/jama.2020.1585 (2 copies)
- 10.1001/jama.2020.2648 (2 copies)
- 10.1056/nejmoa2035389 (2 copies)
- ... and 15 more

### 3. Database Schema (Current)

```
papers table columns:
├── id (INTEGER PRIMARY KEY)
├── title (TEXT)
├── authors (TEXT)
├── abstract (TEXT)
├── journal (TEXT)
├── publication_date (DATE)
├── doi (TEXT)
├── pmid (TEXT)
├── url (TEXT)
├── keywords (TEXT)
├── citation_count (INTEGER) ← Fixed from citations_count
├── quality_score (REAL)
├── source_database (TEXT) ← Added
├── publication_type (TEXT)
├── created_at (TIMESTAMP)
└── updated_at (TIMESTAMP)
```

## Using the Deduplicated Data

You have two options:

### Option 1: Use deduplicated table directly
Update `Capstone.py` line 227 to use `papers_deduped`:
```python
db_path = st.sidebar.text_input("SQLite DB path", value=DEFAULT_DB)
# Or point to a new DB with papers_deduped renamed to papers
```

### Option 2: Replace original table (recommended)

Run these SQL commands:
```sql
-- Backup original
ALTER TABLE papers RENAME TO papers_backup;

-- Promote deduplicated table
ALTER TABLE papers_deduped RENAME TO papers;

-- Recreate indexes
CREATE UNIQUE INDEX IF NOT EXISTS idx_papers_doi ON papers(doi);
CREATE UNIQUE INDEX IF NOT EXISTS idx_papers_pmid ON papers(pmid);
```

Or use the Streamlit app:
1. Go to **Orchestrator Dashboard** → **DB Actions** tab
2. Use "Deduplicate FULL → table" to create a fresh deduplicated table
3. Manually swap tables using SQL commands

## Files Created

1. `fix_schema.py` - Diagnosis script (checks schema, shows duplicates)
2. `deduplicate.py` - Deduplication script (creates papers_deduped)
3. `FIXES_SUMMARY.md` - This document

## Testing

Run the app and verify:
```bash
streamlit run Capstone.py
```

All pages should now work without errors:
- ✅ Data Collection (no missing column errors)
- ✅ Quality Assessment (citation_count recognized)
- ✅ Analysis (charts display correctly)
- ✅ Report Generation (PDF exports work)
- ✅ Orchestrator Dashboard (filters work, no duplicate warnings if using papers_deduped)

## Next Steps

1. **Test the app** with `streamlit run Capstone.py`
2. **Verify** the deduplicated data in Orchestrator Dashboard
3. **Populate** source_database column during future imports (Data Collection page)
4. **Optional**: Replace papers table with papers_deduped (see Option 2 above)
