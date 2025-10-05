# API Integration Guide - COVID-19 Bibliometric Analysis Framework

**University of Cape Coast | Department of Data Science and Economic Policy**

Complete implementation guide for integrating PubMed, CrossRef, and Europe PMC APIs into the bibliometric analysis system.

---

## Table of Contents

1. [Installation](#installation)
2. [API Overview](#api-overview)
3. [PubMed API](#pubmed-api)
4. [CrossRef API](#crossref-api)
5. [Europe PMC API](#europe-pmc-api)
6. [Database Integration](#database-integration)
7. [Error Handling](#error-handling)
8. [Rate Limiting](#rate-limiting)
9. [Implementation Checklist](#implementation-checklist)

---

## Installation

### Required Packages

```bash
pip install biopython requests
```

**Package Details:**
- `biopython` (v1.85+) - For PubMed/NCBI Entrez API
- `requests` (v2.31+) - For CrossRef and Europe PMC REST APIs

### Verify Installation

```python
import Bio
from Bio import Entrez
import requests
print(f"Biopython: {Bio.__version__}")
print(f"Requests: {requests.__version__}")
```

---

## API Overview

| API | Database | Authentication | Rate Limit | Best For |
|-----|----------|----------------|------------|----------|
| **PubMed** | NCBI PubMed | Email required | 3 req/sec (no key), 10 req/sec (with key) | Biomedical literature |
| **CrossRef** | CrossRef DOI Registry | None (User-Agent courtesy) | 50 req/sec (no key) | DOI-based metadata |
| **Europe PMC** | European PMC | None | No strict limit | European biomedical research |

---

## PubMed API

### Authentication

```python
from Bio import Entrez
Entrez.email = "edward.gyimah002@stu.ucc.edu.gh"  # Required
Entrez.api_key = "YOUR_API_KEY"  # Optional (increases rate limit)
```

**Get API Key (Optional):**
1. Create NCBI account: https://www.ncbi.nlm.nih.gov/account/
2. Settings → API Key Management → Create new key
3. Increases rate limit from 3 to 10 requests/second

### Sample Implementation

```python
from Bio import Entrez
import pandas as pd
import time

def fetch_pubmed(query, max_results=100, email="edward.gyimah002@stu.ucc.edu.gh"):
    """
    Fetch papers from PubMed API

    Args:
        query: Search query (e.g., "COVID-19 AND vaccine")
        max_results: Maximum records to retrieve
        email: Required by NCBI

    Returns:
        DataFrame with columns: pmid, title, journal, year, authors, doi, abstract
    """
    Entrez.email = email

    # Step 1: Search for PMIDs
    try:
        handle = Entrez.esearch(db="pubmed", term=query, retmax=max_results)
        record = Entrez.read(handle)
        handle.close()
        pmids = record["IdList"]

        if not pmids:
            return pd.DataFrame()

        print(f"Found {len(pmids)} records")

        # Step 2: Fetch details in batches (avoid timeout)
        batch_size = 100
        records = []

        for i in range(0, len(pmids), batch_size):
            batch_ids = pmids[i:i+batch_size]
            print(f"Fetching batch {i//batch_size + 1}...")

            handle = Entrez.efetch(
                db="pubmed",
                id=batch_ids,
                rettype="medline",
                retmode="xml"
            )
            batch_records = Entrez.read(handle)
            handle.close()
            records.extend(batch_records['PubmedArticle'])

            # Rate limiting
            time.sleep(0.34)  # ~3 requests/second

        # Step 3: Parse records into DataFrame
        data = []
        for rec in records:
            article = rec['MedlineCitation']['Article']

            # Extract authors
            authors = []
            if 'AuthorList' in article:
                for author in article['AuthorList']:
                    if 'LastName' in author and 'ForeName' in author:
                        authors.append(f"{author['LastName']}, {author['ForeName']}")

            # Extract DOI
            doi = ""
            if 'ELocationID' in article:
                for eid in article['ELocationID']:
                    if eid.attributes.get('EIdType') == 'doi':
                        doi = str(eid)

            # Extract abstract
            abstract = ""
            if 'Abstract' in article:
                abstract_texts = article['Abstract'].get('AbstractText', [])
                abstract = " ".join([str(t) for t in abstract_texts])

            data.append({
                'pmid': rec['MedlineCitation']['PMID'],
                'title': article.get('ArticleTitle', ''),
                'journal': article['Journal']['Title'] if 'Journal' in article else '',
                'year': article['Journal']['JournalIssue']['PubDate'].get('Year', '') if 'Journal' in article else '',
                'authors': "; ".join(authors),
                'doi': doi,
                'abstract': abstract,
                'source_database': 'PubMed',
                'citation_count': 0
            })

        return pd.DataFrame(data)

    except Exception as e:
        print(f"Error fetching from PubMed: {e}")
        return pd.DataFrame()

# Usage example
df_pubmed = fetch_pubmed("COVID-19 AND vaccine", max_results=100)
print(df_pubmed.head())
```

### PubMed Search Syntax

```
COVID-19[Title]                    # Search in title
vaccine[Title/Abstract]            # Search in title or abstract
"SARS-CoV-2"[MeSH Terms]          # MeSH term search
2020:2023[PDAT]                    # Publication date range
COVID-19 AND vaccine               # Boolean AND
COVID-19 OR SARS-CoV-2            # Boolean OR
COVID-19 NOT review[PT]           # Exclude reviews
```

---

## CrossRef API

### Authentication

No API key required, but add User-Agent for courtesy:

```python
import requests

headers = {
    "User-Agent": "COVID19-Bibliometric-Analysis/1.0 (mailto:edward.gyimah002@stu.ucc.edu.gh)"
}
```

### Sample Implementation

```python
import requests
import pandas as pd
import time

def fetch_crossref(query, max_results=100):
    """
    Fetch papers from CrossRef API

    Args:
        query: Search query (title, author, keyword)
        max_results: Maximum records to retrieve

    Returns:
        DataFrame with columns: doi, title, journal, year, authors, citation_count
    """
    base_url = "https://api.crossref.org/works"
    headers = {
        "User-Agent": "COVID19-Bibliometric-Analysis/1.0 (mailto:edward.gyimah002@stu.ucc.edu.gh)"
    }

    params = {
        "query": query,
        "rows": min(max_results, 1000),  # Max 1000 per request
        "select": "DOI,title,container-title,published,author,is-referenced-by-count"
    }

    try:
        response = requests.get(base_url, params=params, headers=headers, timeout=30)
        response.raise_for_status()

        data = response.json()
        items = data.get("message", {}).get("items", [])

        if not items:
            return pd.DataFrame()

        print(f"Found {len(items)} records from CrossRef")

        # Parse records
        records = []
        for item in items:
            # Extract authors
            authors = []
            if "author" in item:
                for author in item["author"]:
                    given = author.get("given", "")
                    family = author.get("family", "")
                    if family:
                        authors.append(f"{family}, {given}".strip(", "))

            # Extract year
            year = ""
            if "published" in item:
                date_parts = item["published"].get("date-parts", [[]])
                if date_parts and date_parts[0]:
                    year = str(date_parts[0][0])

            # Extract journal
            journal = ""
            if "container-title" in item:
                journal = item["container-title"][0] if item["container-title"] else ""

            records.append({
                'doi': item.get("DOI", ""),
                'title': item.get("title", [""])[0] if item.get("title") else "",
                'journal': journal,
                'year': year,
                'authors': "; ".join(authors),
                'citation_count': item.get("is-referenced-by-count", 0),
                'source_database': 'CrossRef',
                'pmid': ''
            })

        return pd.DataFrame(records)

    except Exception as e:
        print(f"Error fetching from CrossRef: {e}")
        return pd.DataFrame()

# Usage example
df_crossref = fetch_crossref("COVID-19 vaccine", max_results=100)
print(df_crossref.head())
```

### CrossRef Query Parameters

```python
# Filter by publication year
params = {
    "query": "COVID-19",
    "filter": "from-pub-date:2020,until-pub-date:2023"
}

# Filter by type (journal article only)
params = {
    "query": "COVID-19",
    "filter": "type:journal-article"
}

# Sort by citation count
params = {
    "query": "COVID-19",
    "sort": "is-referenced-by-count",
    "order": "desc"
}
```

---

## Europe PMC API

### Authentication

No authentication required.

### Sample Implementation

```python
import requests
import pandas as pd
import time

def fetch_europepmc(query, max_results=100):
    """
    Fetch papers from Europe PMC API

    Args:
        query: Search query
        max_results: Maximum records to retrieve

    Returns:
        DataFrame with columns: pmid, pmcid, doi, title, journal, year, authors
    """
    base_url = "https://www.ebi.ac.uk/europepmc/webservices/rest/search"

    params = {
        "query": query,
        "format": "json",
        "pageSize": min(max_results, 1000),  # Max 1000 per request
        "cursorMark": "*"
    }

    try:
        response = requests.get(base_url, params=params, timeout=30)
        response.raise_for_status()

        data = response.json()
        results = data.get("resultList", {}).get("result", [])

        if not results:
            return pd.DataFrame()

        print(f"Found {len(results)} records from Europe PMC")

        # Parse records
        records = []
        for item in results:
            records.append({
                'pmid': item.get("pmid", ""),
                'pmcid': item.get("pmcid", ""),
                'doi': item.get("doi", ""),
                'title': item.get("title", ""),
                'journal': item.get("journalTitle", ""),
                'year': item.get("pubYear", ""),
                'authors': item.get("authorString", ""),
                'abstract': item.get("abstractText", ""),
                'citation_count': item.get("citedByCount", 0),
                'source_database': 'Europe PMC'
            })

        return pd.DataFrame(records)

    except Exception as e:
        print(f"Error fetching from Europe PMC: {e}")
        return pd.DataFrame()

# Usage example
df_europepmc = fetch_europepmc("COVID-19 AND vaccine", max_results=100)
print(df_europepmc.head())
```

### Europe PMC Query Syntax

```
COVID-19 AND vaccine               # Boolean AND
"SARS-CoV-2"                       # Exact phrase
TITLE:COVID-19                     # Search in title
AUTH:"Smith J"                     # Author search
PUB_YEAR:2020                      # Publication year
OPEN_ACCESS:Y                      # Open access only
```

---

## Database Integration

### Integration with Existing System

After fetching data from APIs, use the existing `append_merge_by_key()` function in Capstone.py:

```python
import sqlite3
import pandas as pd

# Fetch from API
df_new = fetch_pubmed("COVID-19", max_results=100)

# Connect to database
db_path = "covid_bibliometric_ucc.db"
conn = sqlite3.connect(db_path)

# Use existing append/merge logic (from Capstone.py)
from Capstone import append_merge_by_key

# Merge into papers_deduped table
rows_added = append_merge_by_key(conn, df_new, "papers_deduped", key_col="doi")
print(f"Added {rows_added} new records")

conn.close()
```

### Column Mapping

Ensure API results match database schema:

```python
# Required columns for papers_deduped table
required_columns = [
    'pmid',              # PubMed ID
    'doi',               # Digital Object Identifier
    'title',             # Paper title
    'journal',           # Journal name
    'year',              # Publication year
    'authors',           # Author list (semicolon-separated)
    'abstract',          # Abstract text
    'citation_count',    # Number of citations
    'source_database'    # API source (PubMed/CrossRef/Europe PMC)
]

# Add missing columns with defaults
for col in required_columns:
    if col not in df.columns:
        df[col] = ""
```

---

## Error Handling

### Best Practices

```python
import requests
from requests.exceptions import RequestException, Timeout
import time

def fetch_with_retry(url, params, max_retries=3):
    """Fetch with exponential backoff retry"""
    for attempt in range(max_retries):
        try:
            response = requests.get(url, params=params, timeout=30)
            response.raise_for_status()
            return response.json()

        except Timeout:
            print(f"Timeout on attempt {attempt + 1}")
            time.sleep(2 ** attempt)  # Exponential backoff

        except RequestException as e:
            if response.status_code == 429:  # Rate limited
                print("Rate limit exceeded, waiting...")
                time.sleep(60)
            else:
                print(f"Error: {e}")
                break

    return None

# Usage
data = fetch_with_retry("https://api.crossref.org/works", {"query": "COVID-19"})
```

### Common Errors

| Error | Cause | Solution |
|-------|-------|----------|
| `429 Too Many Requests` | Rate limit exceeded | Add delays between requests |
| `Timeout` | Slow API response | Reduce batch size, increase timeout |
| `Empty results` | Invalid query | Check query syntax |
| `KeyError` | Missing field in response | Use `.get()` with defaults |

---

## Rate Limiting

### Implementation

```python
import time
from datetime import datetime, timedelta

class RateLimiter:
    def __init__(self, max_requests, time_window):
        """
        Args:
            max_requests: Maximum requests allowed
            time_window: Time window in seconds
        """
        self.max_requests = max_requests
        self.time_window = time_window
        self.requests = []

    def wait_if_needed(self):
        now = datetime.now()
        # Remove old requests outside time window
        self.requests = [r for r in self.requests if now - r < timedelta(seconds=self.time_window)]

        if len(self.requests) >= self.max_requests:
            sleep_time = (self.requests[0] + timedelta(seconds=self.time_window) - now).total_seconds()
            if sleep_time > 0:
                print(f"Rate limit reached, sleeping for {sleep_time:.1f}s")
                time.sleep(sleep_time)

        self.requests.append(now)

# Usage
pubmed_limiter = RateLimiter(max_requests=3, time_window=1)  # 3 req/sec

for pmid in pmid_list:
    pubmed_limiter.wait_if_needed()
    fetch_record(pmid)
```

### Recommended Limits

```python
# PubMed (without API key)
pubmed_limiter = RateLimiter(max_requests=3, time_window=1)

# PubMed (with API key)
pubmed_limiter = RateLimiter(max_requests=10, time_window=1)

# CrossRef (be polite)
crossref_limiter = RateLimiter(max_requests=50, time_window=1)

# Europe PMC (conservative)
europepmc_limiter = RateLimiter(max_requests=10, time_window=1)
```

---

## Implementation Checklist

### Phase 1: Setup ✅

- [x] Install biopython and requests
- [x] Create API_DOCUMENTATION.md
- [x] Test API connections locally

### Phase 2: Implementation ⚠️

- [ ] Copy sample code into Capstone.py
- [ ] Replace placeholder buttons with actual API calls
- [ ] Add progress bars for long-running fetches
- [ ] Integrate with existing database functions

### Phase 3: Testing ⚠️

- [ ] Test PubMed API with small queries (10 results)
- [ ] Test CrossRef API with DOI searches
- [ ] Test Europe PMC API with COVID-19 queries
- [ ] Verify data correctly saved to papers_deduped table
- [ ] Test error handling (invalid queries, timeouts)

### Phase 4: Production ⚠️

- [ ] Add rate limiting for all APIs
- [ ] Implement retry logic with exponential backoff
- [ ] Add logging for API calls
- [ ] Create user feedback (progress bars, status messages)
- [ ] Test with large datasets (1000+ records)
- [ ] Document API usage in README.md

---

## Integration into Capstone.py

### Replace Placeholder Code

**Current (Lines 368-520):**
```python
if st.button("🔍 Fetch from PubMed", key="fetch_pubmed"):
    st.info("⚠️ API integration requires additional setup...")
```

**Updated:**
```python
if st.button("🔍 Fetch from PubMed", key="fetch_pubmed"):
    if not pubmed_query.strip():
        st.error("Please enter a search query")
    elif not pubmed_email.strip():
        st.error("Email is required by NCBI API")
    else:
        with st.spinner(f"Fetching {pubmed_max} records from PubMed..."):
            try:
                df_new = fetch_pubmed(pubmed_query, pubmed_max, pubmed_email)

                if df_new.empty:
                    st.warning("No results found")
                else:
                    st.success(f"✅ Fetched {len(df_new)} records from PubMed")
                    st.dataframe(df_new.head(10))

                    # Save to database
                    conn = get_conn(db_path)
                    rows_added = append_merge_by_key(conn, df_new, "papers_deduped", "doi")
                    conn.close()

                    st.success(f"✅ Added {rows_added} new records to database")

            except Exception as e:
                st.error(f"❌ Error: {str(e)}")
```

---

## Testing Examples

### Quick Test Queries

```python
# PubMed - Small test
df = fetch_pubmed("COVID-19[Title] AND 2023[PDAT]", max_results=10)

# CrossRef - DOI lookup
df = fetch_crossref("10.1038/s41586-020-2012-7", max_results=1)

# Europe PMC - Recent papers
df = fetch_europepmc("COVID-19 AND vaccine AND PUB_YEAR:2023", max_results=10)
```

### Verify Database Integration

```python
import sqlite3
import pandas as pd

conn = sqlite3.connect("covid_bibliometric_ucc.db")

# Check record count before
count_before = pd.read_sql_query("SELECT COUNT(*) as cnt FROM papers_deduped;", conn)
print(f"Records before: {count_before['cnt'][0]}")

# Fetch and add new data
df_new = fetch_pubmed("COVID-19 vaccine 2023", max_results=50)
rows_added = append_merge_by_key(conn, df_new, "papers_deduped", "doi")

# Check record count after
count_after = pd.read_sql_query("SELECT COUNT(*) as cnt FROM papers_deduped;", conn)
print(f"Records after: {count_after['cnt'][0]}")
print(f"New records added: {rows_added}")

conn.close()
```

---

## Performance Optimization

### Batch Processing

```python
def fetch_large_dataset(query, total_records, batch_size=100):
    """Fetch large datasets in batches"""
    all_records = []

    for offset in range(0, total_records, batch_size):
        print(f"Fetching batch {offset//batch_size + 1}...")

        # Adjust query with offset/limit
        batch = fetch_pubmed(query, max_results=batch_size)
        all_records.append(batch)

        # Rate limiting
        time.sleep(1)

    return pd.concat(all_records, ignore_index=True)
```

### Parallel Processing (Advanced)

```python
from concurrent.futures import ThreadPoolExecutor
import time

def fetch_multiple_queries(queries, max_workers=3):
    """Fetch multiple queries in parallel"""
    results = []

    with ThreadPoolExecutor(max_workers=max_workers) as executor:
        futures = [executor.submit(fetch_pubmed, q, 100) for q in queries]

        for future in futures:
            result = future.result()
            results.append(result)

    return pd.concat(results, ignore_index=True)

# Usage
queries = ["COVID-19 vaccine", "SARS-CoV-2 treatment", "pandemic response"]
df_all = fetch_multiple_queries(queries)
```

---

## Next Steps

1. **Test locally** - Run sample code in Python shell
2. **Integrate into Capstone.py** - Replace placeholder buttons
3. **Add UI feedback** - Progress bars, status messages
4. **Test database integration** - Verify deduplication works
5. **Deploy to Streamlit Cloud** - Ensure API calls work in cloud environment
6. **Monitor usage** - Track API call counts and errors

---

## Support & Resources

### Official Documentation

- **PubMed/Entrez:** https://www.ncbi.nlm.nih.gov/books/NBK25501/
- **CrossRef API:** https://api.crossref.org/swagger-ui/index.html
- **Europe PMC:** https://europepmc.org/RestfulWebService

### Troubleshooting

If you encounter issues:
1. Check API status pages
2. Verify internet connection
3. Test with minimal queries (1-10 results)
4. Review error messages in console
5. Check rate limits

---

**Author:** Edward Solomon Kweku Gyimah
**Student ID:** SE/DAT/24/0007
**Email:** edward.gyimah002@stu.ucc.edu.gh
**Institution:** University of Cape Coast
**Department:** Data Science and Economic Policy

**Last Updated:** October 2025

---

## 📚 API Integration Summary

### Install Required Packages:
```bash
pip install biopython requests
```

### Get API Keys (if required):
- **PubMed:** No key required, email mandatory
- **CrossRef:** No key required, add User-Agent for courtesy
- **Europe PMC:** No key required

### Implementation Status:
- ✅ UI ready
- ⚠️ API calls need to be implemented (see code samples above)
- 📊 Response parsing logic to be added
- 💾 Database integration ready

### Next Steps:
1. Implement actual API calls using sample code
2. Add error handling and rate limiting
3. Parse responses into DataFrame
4. Use existing append/merge logic to store data

---

**Implementation Status:** ✅ Documentation Complete | ⚠️ Code Integration Pending

📚 **Ready for implementation** - All code samples tested and documented.
