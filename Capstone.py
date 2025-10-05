
# Capstone.py — UCC Bibliometric System (no placeholders)
# Full app: Data Collection • Quality Assessment • Analysis • Report • Orchestrator
import os, re, json, sqlite3, io
from functools import lru_cache

import pandas as pd
import numpy as np
import streamlit as st
import matplotlib.pyplot as plt
try:
    import plotly.express as px
except Exception:
    px = None

from matplotlib.backends.backend_pdf import PdfPages

# -------------------------
# Config
# -------------------------
class UCCProductionConfig:
    def __init__(self):
        self.quality_threshold = int(os.getenv("UCC_QUALITY_THRESHOLD", "97"))
        self.student_name = os.getenv("UCC_STUDENT_NAME", "")
        self.student_id = os.getenv("UCC_STUDENT_ID", "")
        self.student_email = os.getenv("UCC_STUDENT_EMAIL", "")
        self.institution = os.getenv("UCC_INSTITUTION", "University of Cape Coast")
        self.department = os.getenv("UCC_DEPARTMENT", "")
        self.program = os.getenv("UCC_PROGRAM", "")
        self.project_title = os.getenv("UCC_PROJECT_TITLE", "COVID-19 Bibliometric Analysis at UCC")
        self.supervisor = os.getenv("UCC_SUPERVISOR", "")

APP_TITLE = "Capstone — UCC Bibliometric System"
DEFAULT_DB = os.getenv("BIB_DB") or os.path.join(os.path.dirname(__file__), "covid_bibliometric_ucc.db")

st.set_page_config(page_title=APP_TITLE, layout="wide")

# -------------------------
# DB utils
# -------------------------
@lru_cache(maxsize=1)
def get_conn(db_path: str):
    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row
    return conn

def table_exists(conn, name) -> bool:
    q = pd.read_sql_query("SELECT name FROM sqlite_master WHERE type='table' AND name=?;", conn, params=[name])
    return not q.empty

def ensure_papers_schema(conn):
    conn.execute("""
    CREATE TABLE IF NOT EXISTS papers (
        id INTEGER PRIMARY KEY,
        title TEXT,
        journal TEXT,
        publication_date TEXT,
        citations_count INTEGER,
        quality_score REAL,
        source_database TEXT,
        doi TEXT UNIQUE,
        pmid TEXT UNIQUE,
        publication_type TEXT,
        authors TEXT
    );
    """)
    conn.commit()

def schema_for(conn, table):
    try:
        info = pd.read_sql_query(f"PRAGMA table_info([{table}]);", conn)
        return [(r['name'], r['type'] if pd.notna(r['type']) else 'TEXT') for _,r in info.iterrows()]
    except Exception:
        return []

def write_table_preserve(conn, df_, table_name, overwrite=False, create_indexes=True, source_schema='papers'):
    safe = re.sub(r"[^A-Za-z0-9_]", "_", str(table_name))
    if not safe: st.error("Invalid table name."); return False
    table_name = safe
    cur = conn.cursor()
    exists = table_exists(conn, table_name)
    if exists and not overwrite:
        st.error(f"Table '{table_name}' exists. Enable overwrite."); return False
    if exists and overwrite:
        try:
            cur.execute(f"DROP TABLE IF EXISTS [{table_name}];")
        except Exception as e:
            st.error(f"Drop failed: {e}"); return False
    sc = schema_for(conn, source_schema) or [(c,"TEXT") for c in df_.columns]
    ordered = [ (c,t) for (c,t) in sc if c in df_.columns ]
    for c in df_.columns:
        if c not in [x[0] for x in ordered]: ordered.append((c,"TEXT"))
    try:
        cur.execute(f"CREATE TABLE [{table_name}] (" + ", ".join(f"[{c}] {t}" for c,t in ordered) + ");")
    except Exception as e:
        st.error(f"CREATE TABLE failed: {e}"); return False
    if not df_.empty:
        cols = [c for c,_ in ordered]
        try:
            cur.executemany(
                f"INSERT INTO [{table_name}] (" + ", ".join("["+c+"]" for c in cols) + ") VALUES (" + ", ".join(["?"]*len(cols)) + ")",
                df_.reindex(columns=cols).where(pd.notna(df_.reindex(columns=cols)), None).values.tolist()
            )
        except Exception as e:
            st.error(f"INSERT failed: {e}"); return False
    if create_indexes:
        try:
            if "id" in df_.columns:   cur.execute(f"CREATE UNIQUE INDEX IF NOT EXISTS idx_{table_name}_id ON [{table_name}](id);")
            if "doi" in df_.columns:  cur.execute(f"CREATE UNIQUE INDEX IF NOT EXISTS idx_{table_name}_doi ON [{table_name}](doi);")
            if "pmid" in df_.columns: cur.execute(f"CREATE UNIQUE INDEX IF NOT EXISTS idx_{table_name}_pmid ON [{table_name}](pmid);")
        except Exception as e:
            st.warning(f"Index creation warning: {e}")
    conn.commit()
    return True

def sql_create(table, ordered_cols_types):
    return f"CREATE TABLE [{table}] (" + ", ".join(f"[{c}] {t}" for c,t in ordered_cols_types) + ");"

def sql_indexes(table, df_cols):
    stmts = []
    if "id" in df_cols:   stmts.append(f"CREATE UNIQUE INDEX IF NOT EXISTS idx_{table}_id ON [{table}](id);")
    if "doi" in df_cols:  stmts.append(f"CREATE UNIQUE INDEX IF NOT EXISTS idx_{table}_doi ON [{table}](doi);")
    if "pmid" in df_cols: stmts.append(f"CREATE UNIQUE INDEX IF NOT EXISTS idx_{table}_pmid ON [{table}](pmid);")
    return stmts

def sql_insert_on_conflict(table, cols, key):
    cols_br = ", ".join("["+c+"]" for c in cols)
    placeholders = ", ".join(["?"]*len(cols))
    set_clause = ", ".join(f"[{c}]=excluded.[{c}]" for c in cols if c != key)
    return f"INSERT INTO [{table}] ({cols_br}) VALUES ({placeholders}) ON CONFLICT([{key}]) DO UPDATE SET {set_clause};"

def append_merge_by_key(conn, df_, table, key):
    cur = conn.cursor()
    try:
        cur.execute(f"CREATE UNIQUE INDEX IF NOT EXISTS idx_{table}_{key} ON [{table}]([{key}]);")
    except Exception:
        pass
    cols = list(df_.columns)
    sql = sql_insert_on_conflict(table, cols, key)
    cur.executemany(sql, df_.where(pd.notna(df_), None).values.tolist())
    conn.commit()
    return len(df_)

# -------------------------
# Domain helpers
# -------------------------
def parse_year(x):
    if pd.isna(x): return None
    s = str(x)
    if len(s) >= 4 and s[:4].isdigit():
        return int(s[:4])
    return None

def normalize_authors(val):
    if val is None or (isinstance(val, float) and np.isnan(val)): return []
    if isinstance(val, (list, tuple)): return [str(a).strip() for a in val if str(a).strip()]
    s = str(val).strip()
    if not s: return []
    try:
        parsed = json.loads(s)
        if isinstance(parsed, list): return [str(a).strip() for a in parsed if str(a).strip()]
    except Exception: pass
    if ";" in s: return [p.strip() for p in s.split(";") if p.strip()]
    if "," in s:
        parts = [p.strip() for p in s.split(";")]
        if len(parts) > 1:
            out = []
            for seg in parts: out.extend([x.strip() for x in seg.split(",") if x.strip()])
            return out
        else:
            return [p.strip() for p in s.split(",") if p.strip()]
    return [s]

def build_key(row):
    for k in ("doi","pmid"):
        if k in row and pd.notna(row[k]) and str(row[k]).strip(): return str(row[k]).strip().lower()
    t = str(row.get("title","")).strip().lower()
    return " ".join(t.split())

def to_ris(df: pd.DataFrame) -> str:
    lines = []
    for _, r in df.iterrows():
        ty = "JOUR"
        if "publication_type" in r and pd.notna(r["publication_type"]):
            pt = str(r["publication_type"]).lower()
            if "preprint" in pt: ty = "UNPB"
            elif "conference" in pt: ty = "CPAPER"
        lines.append(f"TY  - {ty}")
        if pd.notna(r.get("title")):  lines.append(f"TI  - {r['title']}")
        if pd.notna(r.get("journal")):lines.append(f"JO  - {r['journal']}")
        y = parse_year(r.get("publication_date")) if pd.notna(r.get("publication_date")) else None
        if y: lines.append(f"PY  - {y}")
        if pd.notna(r.get("doi")):   lines.append(f"DO  - {r['doi']}")
        if pd.notna(r.get("pmid")):  lines.append(f"ID  - {r['pmid']}")
        au_col = next((c for c in ["authors","author_list","creators","creator"] if c in r.index), None)
        if au_col:
            for au in normalize_authors(r[au_col]):
                lines.append(f"AU  - {au}")
        lines.append("ER  - ")
        lines.append("")
    return "\n".join(lines)

def to_bibtex(df: pd.DataFrame) -> str:
    entries = []
    for i, r in df.iterrows():
        key = (str(r.get("doi")) or str(r.get("pmid")) or f"paper{i}").replace("/", "_")
        etype = "article"
        y = parse_year(r.get("publication_date")) if "publication_date" in r.index else None
        fields = []
        if pd.notna(r.get("title")):   fields.append(f"  title = {{{r['title']}}}")
        if pd.notna(r.get("journal")): fields.append(f"  journal = {{{r['journal']}}}")
        if y:                          fields.append(f"  year = {{{y}}}")
        if pd.notna(r.get("doi")):     fields.append(f"  doi = {{{r['doi']}}}")
        if pd.notna(r.get("pmid")):    fields.append(f"  pmid = {{{r['pmid']}}}")
        au_col = next((c for c in ["authors","author_list","creators","creator"] if c in r.index), None)
        if au_col:
            au = normalize_authors(r[au_col])
            if au: fields.append("  author = {" + " and ".join(au) + "}")
        entry = "@{etype}{{{key},\n{fields}\n}}".format(etype=etype, key=key, fields=", ".join(fields))
        entries.append(entry)
    return "\n\n".join(entries)

# -------------------------
# Sidebar: DB path
# -------------------------
st.sidebar.header("Data Source")
db_path = st.sidebar.text_input("SQLite DB path", value=DEFAULT_DB)
conn = get_conn(db_path)
ensure_papers_schema(conn)

# -------------------------
# Page: Data Collection
# -------------------------
def render_data_collection():
    st.header("Data Collection")
    st.caption("Upload CSV → map columns → preview → append/merge into DB; also dedupe full corpus.")

    uploaded = st.file_uploader("Upload bibliometric CSV", type=["csv"])
    if uploaded:
        try:
            df_up = pd.read_csv(uploaded)
        except Exception as e:
            st.error(f"Failed to read CSV: {e}")
            return
        st.subheader("Preview")
        st.dataframe(df_up.head(100))

        # Simple mapping UI
        st.subheader("Column Mapping")
        cols = df_up.columns.tolist()
        def pick(label, default):
            options = ["-- none --"] + cols
            idx = options.index(default) if default in options else 0
            return st.selectbox(label, options, index=idx)

        m_title  = pick("Title", "title")
        m_journ  = pick("Journal", "journal")
        m_date   = pick("Publication Date (YYYY...)", "publication_date")
        m_cit    = pick("Citations", "citations_count")
        m_src    = pick("Source Database", "source_database")
        m_doi    = pick("DOI", "doi")
        m_pmid   = pick("PMID", "pmid")
        m_ptype  = pick("Publication Type", "publication_type")
        m_auth   = pick("Authors (string or list)", "authors")

        def map_df(dfin):
            out = pd.DataFrame()
            def get(c): return None if c=="-- none --" else dfin.get(c)
            out["title"] = get(m_title)
            out["journal"] = get(m_journ)
            out["publication_date"] = get(m_date)
            out["citations_count"] = pd.to_numeric(get(m_cit), errors="coerce") if get(m_cit) is not None else None
            out["source_database"] = get(m_src)
            out["doi"] = get(m_doi)
            out["pmid"] = get(m_pmid)
            out["publication_type"] = get(m_ptype)
            out["authors"] = get(m_auth)
            return out

        mapped = map_df(df_up)
        st.subheader("Mapped Preview")
        st.dataframe(mapped.head(100))

        st.subheader("Append/Merge")
        target = st.text_input("Target table", value="papers")
        use_doi = st.checkbox("Use DOI as merge key", value=True)
        use_pmid = st.checkbox("Use PMID as merge key", value=True)
        if st.button("Append/Merge into DB"):
            if mapped.empty:
                st.error("No data to write.")
            else:
                # create shell if absent
                if not table_exists(conn, target):
                    ok = write_table_preserve(conn, mapped.head(0), target, overwrite=True)
                    if not ok: st.error("Failed to create target table."); return
                # perform merges
                total = 0
                if use_doi and "doi" in mapped.columns:
                    df_doi = mapped[mapped["doi"].notna() & (mapped["doi"].astype(str)!="")]
                    if not df_doi.empty:
                        total += append_merge_by_key(conn, df_doi, target, "doi")
                if use_pmid and "pmid" in mapped.columns:
                    df_pmid = mapped[mapped["pmid"].notna() & (mapped["pmid"].astype(str)!="")]
                    if not df_pmid.empty:
                        total += append_merge_by_key(conn, df_pmid, target, "pmid")
                st.success(f"Append/Merge completed. Processed rows: {total:,}.")

    st.divider()
    st.subheader("Deduplicate FULL 'papers' → new table")
    new_name = st.text_input("New table name", value="papers_dedup_dc")
    if st.button("Run dedupe (by DOI→PMID→Title)"):
        full = pd.read_sql_query("SELECT * FROM papers;", conn)
        if full.empty:
            st.error("No data in 'papers'.")
        else:
            keys = [build_key(r) for _, r in full.iterrows()]
            out = full.assign(_k=keys).drop_duplicates("_k").drop(columns=["_k"])
            overwrite = False
            exists = table_exists(conn, new_name)
            if exists:
                st.warning(f"Table {new_name} exists. Tick to overwrite.")
                overwrite = st.checkbox("Yes, overwrite", key="dc_over")
            if overwrite or not exists:
                ok = write_table_preserve(conn, out, new_name, overwrite=overwrite)
                if ok: st.success(f"Created table '{new_name}' with {len(out):,} rows.")

# -------------------------
# Page: Quality Assessment
# -------------------------
def render_quality():
    st.header("Quality Assessment")
    st.caption("Compute/update quality_score; write back to DB.")
    df = pd.read_sql_query("SELECT * FROM papers;", conn)
    if df.empty:
        st.info("No data in 'papers'."); return

    # Basic heuristic scoring
    st.subheader("Quality Model")
    w_doi   = st.slider("Weight: has DOI", 0.0, 2.0, 0.5, 0.1)
    w_cit   = st.slider("Weight: citations (normalized)", 0.0, 2.0, 1.0, 0.1)
    w_rec   = st.slider("Weight: recency (year)", 0.0, 2.0, 0.7, 0.1)
    w_jour  = st.slider("Weight: has Journal", 0.0, 2.0, 0.3, 0.1)

    # compute year
    if "publication_date" in df.columns:
        df["year"] = df["publication_date"].apply(parse_year)
    else:
        df["year"] = None
    y_now = pd.Timestamp.utcnow().year
    cit = pd.to_numeric(df.get("citations_count", pd.Series([np.nan]*len(df))), errors="coerce")
    cit_norm = (cit - np.nanmin(cit)) / (np.nanmax(cit) - np.nanmin(cit)) if np.nanmax(cit) != np.nanmin(cit) else 0
    rec = (df["year"].fillna(y_now) - df["year"].fillna(y_now).min()) / max(1, (df["year"].fillna(y_now).max() - df["year"].fillna(y_now).min()))
    score = 100*(w_doi*(df["doi"].notna() & (df["doi"].astype(str)!="")).astype(float)
                 + w_cit*pd.to_numeric(cit_norm if not isinstance(cit_norm,int) else 0)
                 + w_rec*pd.to_numeric(rec if not isinstance(rec,int) else 0)
                 + w_jour*(df["journal"].notna() & (df["journal"].astype(str)!="")).astype(float))
    # normalize to 0-100
    if isinstance(score, pd.Series):
        m, M = float(score.min()), float(score.max())
        if M>m: score = (score - m) / (M - m) * 100.0
        else: score = score.fillna(0.0)
    df["quality_score_new"] = score.round(2)

    st.subheader("Preview")
    cols = [c for c in ["title","journal","publication_date","citations_count","doi","pmid","quality_score","quality_score_new"] if c in df.columns or c=="quality_score_new"]
    st.dataframe(df[cols].head(200))

    if st.button("Write quality_score to DB (UPDATE)"):
        cur = conn.cursor()
        # ensure column exists
        try:
            cur.execute("ALTER TABLE papers ADD COLUMN quality_score REAL;")
        except Exception:
            pass
        # update using rowid mapping: safer with primary key id or doi/pmid
        if "id" in df.columns and df["id"].notna().any():
            for _id, val in zip(df["id"], df["quality_score_new"]):
                cur.execute("UPDATE papers SET quality_score=? WHERE id=?", (float(val) if pd.notna(val) else None, int(_id)))
        else:
            # fallback: by doi
            for doi, val in zip(df["doi"], df["quality_score_new"]):
                if pd.notna(doi) and str(doi).strip():
                    cur.execute("UPDATE papers SET quality_score=? WHERE doi=?", (float(val) if pd.notna(val) else None, str(doi)))
        conn.commit()
        st.success("quality_score updated.")

# -------------------------
# Page: Analysis
# -------------------------
def render_analysis():
    st.header("Analysis")
    df = pd.read_sql_query("SELECT * FROM papers;", conn)
    if df.empty:
        st.info("No data in 'papers'."); return

    if "publication_date" in df.columns:
        df["year"] = df["publication_date"].apply(parse_year)
    else:
        df["year"] = None
    for col in ["citations_count","quality_score"]:
        if col in df.columns:
            df[col] = pd.to_numeric(df[col], errors="coerce")

    c1,c2,c3 = st.columns(3)
    with c1: st.metric("Total papers", f"{len(df):,}")
    with c2:
        if df["year"].notna().any(): st.metric("Year span", f"{int(df['year'].min())}–{int(df['year'].max())}")
        else: st.metric("Year span", "—")
    with c3:
        if "citations_count" in df.columns and df["citations_count"].notna().any(): st.metric("Avg citations", f"{df['citations_count'].mean():.1f}")
        else: st.metric("Avg citations", "—")

    st.subheader("Publications per Year")
    if df["year"].notna().any():
        yearly = df.groupby("year").size().reset_index(name="count").sort_values("year")
        try:
            st.plotly_chart(px.line(yearly, x="year", y="count", markers=True), use_container_width=True)
        except Exception:
            st.line_chart(yearly.set_index("year"))

    st.subheader("Top Journals")
    if "journal" in df.columns:
        jv = df["journal"].dropna().astype(str).value_counts().head(30).reset_index()
        jv.columns = ["journal","count"]
        try:
            st.plotly_chart(px.bar(jv, x="journal", y="count"), use_container_width=True)
        except Exception:
            st.bar_chart(jv.set_index("journal"))

    st.subheader("Source Distribution")
    if "source_database" in df.columns:
        sv = df["source_database"].dropna().astype(str).value_counts().reset_index()
        sv.columns = ["source_database","count"]
        try:
            st.plotly_chart(px.bar(sv, x="source_database", y="count"), use_container_width=True)
        except Exception:
            st.bar_chart(sv.set_index("source_database"))

    st.subheader("Top Cited")
    if "citations_count" in df.columns:
        topc = df.sort_values("citations_count", ascending=False).head(200)
        cols = [c for c in ["title","journal","year","citations_count","doi","pmid"] if c in topc.columns]
        st.dataframe(topc[cols].fillna("").head(200))

# -------------------------
# Page: Report Generation
# -------------------------
def render_report():
    st.header("Report Generation")
    st.caption("Generate a multi-page PDF (cover, yearly trend, source mix, top journals, top-cited).")
    df = pd.read_sql_query("SELECT * FROM papers;", conn)
    if df.empty:
        st.info("No data in 'papers'."); return
    if "publication_date" in df.columns:
        df["year"] = df["publication_date"].apply(parse_year)
    else: df["year"] = None
    for col in ["citations_count","quality_score"]:
        if col in df.columns:
            df[col] = pd.to_numeric(df[col], errors="coerce")

    cfg = UCCProductionConfig()
    out_dir = os.path.join(os.path.dirname(__file__), "reports")
    os.makedirs(out_dir, exist_ok=True)
    import datetime as _dt
    ts = _dt.datetime.utcnow().strftime("%Y%m%d_%H%M%SZ")
    pdf_path = os.path.join(out_dir, f"ucc_biblio_report_{ts}.pdf")

    if st.button("Generate PDF now"):
        with PdfPages(pdf_path) as pdf:
            # Cover
            fig = plt.figure(figsize=(8.27, 11.69)); ax = fig.add_subplot(111); ax.axis('off')
            ax.set_title("UCC COVID-19 Bibliometric Report", pad=20, fontsize=16, weight='bold')
            lines = [
                f"Student: {cfg.student_name or '—'}  •  ID: {cfg.student_id or '—'}",
                f"Email: {cfg.student_email or '—'}",
                f"Institution: {cfg.institution or '—'}",
                f"Department: {cfg.department or '—'}",
                f"Programme: {cfg.program or '—'}",
                f"Project Title: {cfg.project_title or '—'}",
                f"Supervisor: {cfg.supervisor or '—'}",
                "",
                f"Records: {len(df):,}",
            ]
            if df["year"].notna().any(): lines.append(f"Year span: {int(df['year'].min())}–{int(df['year'].max())}")
            if "citations_count" in df.columns and df["citations_count"].notna().any(): lines.append(f"Avg citations: {df['citations_count'].mean():.2f}")
            if "quality_score" in df.columns and df["quality_score"].notna().any(): lines.append(f"Avg quality: {df['quality_score'].mean():.2f} (threshold {cfg.quality_threshold})")
            y = 0.85
            for ln in lines: ax.text(0.02, y, ln, transform=ax.transAxes, fontsize=11, va='top'); y -= 0.05
            pdf.savefig(fig); plt.close(fig)

            if df["year"].notna().any():
                yearly = df.groupby("year").size().reset_index(name="count").sort_values("year")
                fig = plt.figure(figsize=(8.27, 11.69)); ax = fig.add_subplot(111)
                ax.plot(yearly["year"], yearly["count"], marker="o"); ax.set_title("Publications per Year"); ax.set_xlabel("Year"); ax.set_ylabel("Count")
                pdf.savefig(fig); plt.close(fig)

            if "source_database" in df.columns and not df["source_database"].isna().all():
                srcv = df["source_database"].value_counts().head(20)
                fig = plt.figure(figsize=(8.27, 11.69)); ax = fig.add_subplot(111)
                ax.bar(srcv.index.astype(str), srcv.values); ax.set_title("Source Distribution (Top 20)")
                ax.set_xticklabels(srcv.index.astype(str), rotation=45, ha="right"); ax.set_ylabel("Count"); fig.tight_layout()
                pdf.savefig(fig); plt.close(fig)

            if "journal" in df.columns and not df["journal"].isna().all():
                jv = df["journal"].value_counts().head(20)
                fig = plt.figure(figsize=(8.27, 11.69)); ax = fig.add_subplot(111)
                ax.bar(jv.index.astype(str), jv.values); ax.set_title("Top Journals (Top 20)")
                ax.set_xticklabels(jv.index.astype(str), rotation=45, ha="right"); ax.set_ylabel("Count"); fig.tight_layout()
                pdf.savefig(fig); plt.close(fig)

            if "citations_count" in df.columns and df["citations_count"].notna().any():
                topc = df.sort_values("citations_count", ascending=False).head(20)
                fig = plt.figure(figsize=(8.27, 11.69)); ax = fig.add_subplot(111); ax.axis('off'); ax.set_title("Top 20 by Citations", pad=20)
                cols = [c for c in ["title","journal","year","citations_count"] if c in topc.columns]
                table_data = [cols] + topc[cols].astype(str).values.tolist()
                table = ax.table(cellText=table_data, loc='center'); table.auto_set_font_size(False); table.set_fontsize(8); table.scale(1,1.2)
                pdf.savefig(fig); plt.close(fig)

        try:
            with open(pdf_path, "rb") as fh:
                st.download_button("Download PDF", data=fh.read(), file_name=os.path.basename(pdf_path), mime="application/pdf")
        except Exception as e:
            st.info(f"PDF saved at: {pdf_path}")
            st.error(f"Auto-download failed: {e}")

# -------------------------
# Page: Orchestrator Dashboard (full)
# -------------------------
def render_orchestrator_dashboard():
    st.header("🧭 Orchestrator Dashboard")
    st.caption("Filter • Explore • Export • Write-backs • Dry-Run • Append/Merge • PDF")

    df = pd.read_sql_query("SELECT * FROM papers;", conn)
    if "publication_date" in df.columns:
        df["year"] = df["publication_date"].apply(parse_year)
    else:
        df["year"] = None
    for col in ["citations_count","quality_score"]:
        if col in df.columns:
            df[col] = pd.to_numeric(df[col], errors="coerce")

    # Filters
    st.sidebar.header("Filters")
    years = sorted([int(y) for y in df["year"].dropna().unique().tolist()])
    sel_years = st.sidebar.multiselect("Year", years, default=years[-10:] if years else [])

    if "journal" in df.columns:
        top_journals = df["journal"].dropna().astype(str).value_counts().head(50).index.tolist()
        sel_journals = st.sidebar.multiselect("Journal (top 50)", top_journals, default=[])
    else:
        sel_journals = []

    if "source_database" in df.columns:
        srcs = sorted(df["source_database"].dropna().astype(str).unique().tolist())
        sel_sources = st.sidebar.multiselect("Source", srcs, default=[])
    else:
        sel_sources = []

    cit_range = None
    if "citations_count" in df.columns and df["citations_count"].notna().any():
        cmin, cmax = int(np.nanmin(df["citations_count"])), int(np.nanmax(df["citations_count"]))
        cmin = min(cmin, 0); cmax = max(cmax, 0)
        cit_range = st.sidebar.slider("Citations range", min_value=cmin, max_value=cmax, value=(cmin, cmax))

    qual_range = None
    if "quality_score" in df.columns and df["quality_score"].notna().any():
        qmin, qmax = float(np.nanmin(df["quality_score"])), float(np.nanmax(df["quality_score"]))
        qmin = 0.0 if np.isnan(qmin) else float(qmin)
        qmax = 100.0 if np.isnan(qmax) else float(qmax)
        qual_range = st.sidebar.slider("Quality score range", min_value=float(0.0), max_value=float(100.0), value=(qmin, qmax))

    search_text = st.sidebar.text_input("Search title contains", value="")

    f = df.copy()
    if sel_years: f = f[f["year"].isin(sel_years)]
    if sel_journals and "journal" in f.columns: f = f[f["journal"].astype(str).isin(sel_journals)]
    if sel_sources and "source_database" in f.columns: f = f[f["source_database"].astype(str).isin(sel_sources)]
    if cit_range and "citations_count" in f.columns: f = f[(f["citations_count"].fillna(0)>=cit_range[0]) & (f["citations_count"].fillna(0)<=cit_range[1])]
    if qual_range and "quality_score" in f.columns: f = f[(f["quality_score"].fillna(0)>=qual_range[0]) & (f["quality_score"].fillna(0)<=qual_range[1])]
    if search_text.strip(): f = f[f["title"].astype(str).str.lower().str.contains(search_text.strip().lower(), na=False)]

    # KPIs
    c1,c2,c3,c4 = st.columns(4)
    with c1: st.metric("Papers (filtered)", f"{len(f):,}")
    with c2:
        if f["year"].notna().any(): st.metric("Year span", f"{int(f['year'].min())}–{int(f['year'].max())}")
        else: st.metric("Year span", "—")
    with c3:
        if "citations_count" in f.columns and f["citations_count"].notna().any(): st.metric("Avg citations", f"{f['citations_count'].mean():.1f}")
        else: st.metric("Avg citations", "—")
    with c4:
        if "journal" in f.columns and not f["journal"].isna().all(): st.metric("Top journal", f["journal"].value_counts().idxmax())
        else: st.metric("Top journal", "—")

    # Tabs
    t1, t2, t3, t4, t5, t6, t7, t8 = st.tabs(["Overview","Sources","Journals","Top-Cited","Duplicates","Exports","DB Actions","Report PDF"])

    with t1:
        if f.empty: st.info("No data for current filters.")
        else:
            if f["year"].notna().any():
                yearly = f.groupby("year").size().reset_index(name="count").sort_values("year")
                try:
                    st.plotly_chart(px.line(yearly, x="year", y="count", markers=True, title="Publications per Year"), use_container_width=True)
                except Exception:
                    st.line_chart(yearly.set_index("year"))
            st.dataframe(f.head(200))

    with t2:
        if "source_database" in f.columns and not f.empty:
            srcv = f["source_database"].value_counts().reset_index()
            srcv.columns = ["source_database","count"]
            try:
                st.plotly_chart(px.bar(srcv, x="source_database", y="count", title="Source Distribution"), use_container_width=True)
            except Exception:
                st.bar_chart(srcv.set_index("source_database"))
            st.dataframe(srcv)
        else: st.info("No 'source_database' column.")

    with t3:
        if "journal" in f.columns and not f.empty:
            jv = f["journal"].value_counts().head(50).reset_index()
            jv.columns = ["journal","count"]
            try:
                st.plotly_chart(px.bar(jv, x="journal", y="count", title="Top Journals (Top 50)"), use_container_width=True)
            except Exception:
                st.bar_chart(jv.set_index("journal"))
            st.dataframe(jv)
        else: st.info("No 'journal' column.")

    with t4:
        if "citations_count" in f.columns and not f.empty:
            topc = f.sort_values("citations_count", ascending=False).head(200)
            cols = [c for c in ["title","journal","year","citations_count","doi","pmid"] if c in topc.columns]
            st.dataframe(topc[cols].fillna("").head(200))
        else: st.info("No 'citations_count' column.")

    with t5:
        k = f.apply(lambda r: build_key(r), axis=1)
        dups = f.assign(_k=k).groupby("_k").size().reset_index(name="count")
        dups = dups[dups["count"]>1].sort_values("count", ascending=False)
        st.success("No duplicates by key.") if dups.empty else (st.warning(f"Potential duplicates: {len(dups)} keys"), st.dataframe(dups.head(1000)))

    with t6:
        st.subheader("Export current filtered set")
        preview_cols = [c for c in ["title","journal","year","doi","pmid","citations_count","quality_score","source_database"] if c in f.columns]
        st.dataframe(f[preview_cols].head(200))
        st.download_button("Download CSV", data=f.to_csv(index=False).encode("utf-8"), file_name="ucc_filtered.csv", mime="text/csv")
        st.download_button("Download RIS", data=to_ris(f).encode("utf-8"), file_name="ucc_filtered.ris", mime="application/x-research-info-systems")
        st.download_button("Download BibTeX", data=to_bibtex(f).encode("utf-8"), file_name="ucc_filtered.bib", mime="application/x-bibtex")

    with t7:
        st.subheader("Write-Back Actions")
        st.caption("Non-destructive writes. Confirm overwrite when writing to an existing table.")
        tabA, tabB, tabC, tabD, tabE = st.tabs(["Deduplicate FULL → table","Materialize FILTERED → table","Quality ≥ threshold → table","Dry-Run SQL Preview","Append/Merge by DOI/PMID"])

        with tabA:
            new_name = st.text_input("New table name", value="papers_dedup")
            if st.button("Run dedupe and write", key="dedupe_run"):
                full = pd.read_sql_query("SELECT * FROM papers;", conn)
                if full.empty: st.error("No data found in 'papers'.")
                else:
                    keys = [build_key(r) for _,r in full.iterrows()]
                    out = full.assign(_k=keys).drop_duplicates("_k").drop(columns=["_k"])
                    overwrite = False
                    if table_exists(conn, new_name):
                        st.warning(f"Table {new_name} exists. Tick to overwrite.")
                        overwrite = st.checkbox("Yes, overwrite", key="dedupe_over")
                    if overwrite or not table_exists(conn, new_name):
                        ok = write_table_preserve(conn, out, new_name, overwrite=overwrite)
                        if ok: st.success(f"Created table '{new_name}' with {len(out):,} rows.")

        with tabB:
            mat_name = st.text_input("New table name", value="papers_view_materialized")
            if st.button("Write filtered to table", key="materialize_run"):
                overwrite = False
                if table_exists(conn, mat_name):
                    st.warning(f"Table {mat_name} exists. Tick to overwrite.")
                    overwrite = st.checkbox("Yes, overwrite", key="materialize_over")
                if overwrite or not table_exists(conn, mat_name):
                    ok = write_table_preserve(conn, f, mat_name, overwrite=overwrite)
                    if ok: st.success(f"Created table '{mat_name}' with {len(f):,} rows.")

        with tabC:
            cfg = UCCProductionConfig()
            thr = st.slider("Quality threshold", min_value=0, max_value=100, value=cfg.quality_threshold, step=1)
            qname = st.text_input("New table name", value=f"papers_quality_ge_{thr}")
            if st.button("Write quality-filtered table", key="quality_run"):
                full = pd.read_sql_query("SELECT * FROM papers;", conn)
                if "quality_score" not in full.columns: st.error("No 'quality_score' column found.")
                else:
                    qdf = full[full["quality_score"].fillna(0) >= thr].copy()
                    overwrite = False
                    if table_exists(conn, qname):
                        st.warning(f"Table {qname} exists. Tick to overwrite.")
                        overwrite = st.checkbox("Yes, overwrite", key="quality_over")
                    if overwrite or not table_exists(conn, qname):
                        ok = write_table_preserve(conn, qdf, qname, overwrite=overwrite)
                        if ok: st.success(f"Created table '{qname}' with {len(qdf):,} rows (quality >= {thr}).")

        with tabD:
            st.write("Preview SQL that would run (CREATE/INDEX/INSERT). No DB changes.")
            action = st.selectbox("Action", ["Deduplicate FULL","Materialize FILTERED","Quality ≥ threshold"])
            p_name = st.text_input("Preview table name", value="preview_table")
            thr_prev = st.slider("Quality threshold (for Quality action)", min_value=0, max_value=100, value=97, step=1, key="q_prev")
            if st.button("Generate Preview", key="dry_run_btn"):
                if action == "Deduplicate FULL":
                    full = pd.read_sql_query("SELECT * FROM papers;", conn)
                    if full.empty:
                        st.info("No rows in papers.")
                        dprev = pd.DataFrame()
                    else:
                        keys = [build_key(r) for _,r in full.iterrows()]
                        dprev = full.assign(_k=keys).drop_duplicates("_k").drop(columns=["_k"])
                elif action == "Materialize FILTERED":
                    dprev = f.copy()
                else:
                    full = pd.read_sql_query("SELECT * FROM papers;", conn)
                    if "quality_score" not in full.columns: st.error("No 'quality_score' column found."); dprev = pd.DataFrame()
                    else: dprev = full[full["quality_score"].fillna(0) >= thr_prev].copy()
                if dprev.empty: st.info("No rows in resulting DataFrame.")
                else:
                    sc = schema_for(conn, "papers") or [(c,"TEXT") for c in dprev.columns]
                    ordered = [ (c,t) for (c,t) in sc if c in dprev.columns ]
                    for c in dprev.columns:
                        if c not in [x[0] for x in ordered]: ordered.append((c,"TEXT"))
                    st.code(sql_create(p_name, ordered), language="sql")
                    for stmt in sql_indexes(p_name, dprev.columns): st.code(stmt, language="sql")
                    key = "doi" if "doi" in dprev.columns else ("pmid" if "pmid" in dprev.columns else ordered[0][0])
                    st.write(f"Rows to insert: **{len(dprev):,}** — conflict key preview: `{key}`")
                    st.code(sql_insert_on_conflict(p_name, [c for c,_ in ordered], key), language="sql")

        with tabE:
            st.write("Append/Merge current filtered data into a target table by DOI/PMID (no drop).")
            target = st.text_input("Target table name", value="papers")
            create_shell = st.checkbox("Create target table if missing (schema from 'papers')", value=True)
            use_doi = "doi" in df.columns and st.checkbox("Use DOI as merge key", value=True)
            use_pmid = "pmid" in df.columns and st.checkbox("Use PMID as merge key", value=True)
            if st.button("Run Append/Merge", key="append_run"):
                if f.empty: st.error("Filtered set is empty.")
                else:
                    exists = table_exists(conn, target)
                    if not exists and create_shell:
                        ok = write_table_preserve(conn, f.head(0), target, overwrite=True)  # shell create
                        if not ok: st.error("Failed to create target table."); st.stop()
                    exists2 = table_exists(conn, target)
                    if not exists2: st.error("Target table does not exist."); st.stop()
                    total = 0
                    if use_doi and "doi" in f.columns:
                        df_doi = f[f['doi'].notna() & (f['doi'].astype(str)!='')]
                        if not df_doi.empty:
                            total += append_merge_by_key(conn, df_doi, target, "doi")
                    if use_pmid and "pmid" in f.columns:
                        df_pmid = f[f['pmid'].notna() & (f['pmid'].astype(str)!='')]
                        if not df_pmid.empty:
                            total += append_merge_by_key(conn, df_pmid, target, "pmid")
                    if not use_doi and not use_pmid:
                        st.warning("No merge key selected; nothing done.")
                    else:
                        st.success(f"Append/Merge completed. Processed rows: {total:,}.")

    with t8:
        st.subheader("Generate PDF Report (filtered set)")
        # Windows-friendly output path
        out_dir = os.path.join(os.path.dirname(__file__), "reports")
        os.makedirs(out_dir, exist_ok=True)
        import datetime as _dt
        ts = _dt.datetime.utcnow().strftime("%Y%m%d_%H%M%SZ")
        pdf_path = os.path.join(out_dir, f"ucc_biblio_report_{ts}.pdf")
        cfg = UCCProductionConfig()
        if st.button("Generate PDF now"):
            with PdfPages(pdf_path) as pdf:
                # Cover
                fig = plt.figure(figsize=(8.27, 11.69)); ax = fig.add_subplot(111); ax.axis('off')
                ax.set_title("UCC COVID-19 Bibliometric Report", pad=20, fontsize=16, weight='bold')
                lines = [
                    f"Student: {cfg.student_name or '—'}  •  ID: {cfg.student_id or '—'}",
                    f"Email: {cfg.student_email or '—'}",
                    f"Institution: {cfg.institution or '—'}",
                    f"Department: {cfg.department or '—'}",
                    f"Programme: {cfg.program or '—'}",
                    f"Project Title: {cfg.project_title or '—'}",
                    f"Supervisor: {cfg.supervisor or '—'}",
                    "",
                    f"Records (filtered): {len(f):,}",
                ]
                if f["year"].notna().any(): lines.append(f"Year span: {int(f['year'].min())}–{int(f['year'].max())}")
                if "citations_count" in f.columns and f["citations_count"].notna().any(): lines.append(f"Avg citations: {f['citations_count'].mean():.2f}")
                if "quality_score" in f.columns and f["quality_score"].notna().any(): lines.append(f"Avg quality: {f['quality_score'].mean():.2f} (threshold {cfg.quality_threshold})")
                y = 0.85
                for ln in lines: ax.text(0.02, y, ln, transform=ax.transAxes, fontsize=11, va='top'); y -= 0.05
                pdf.savefig(fig); plt.close(fig)

                if f["year"].notna().any():
                    yearly = f.groupby("year").size().reset_index(name="count").sort_values("year")
                    fig = plt.figure(figsize=(8.27, 11.69)); ax = fig.add_subplot(111)
                    ax.plot(yearly["year"], yearly["count"], marker="o"); ax.set_title("Publications per Year"); ax.set_xlabel("Year"); ax.set_ylabel("Count")
                    pdf.savefig(fig); plt.close(fig)

                if "source_database" in f.columns and not f["source_database"].isna().all():
                    srcv = f["source_database"].value_counts().head(20)
                    fig = plt.figure(figsize=(8.27, 11.69)); ax = fig.add_subplot(111)
                    ax.bar(srcv.index.astype(str), srcv.values); ax.set_title("Source Distribution (Top 20)")
                    ax.set_xticklabels(srcv.index.astype(str), rotation=45, ha="right"); ax.set_ylabel("Count"); fig.tight_layout()
                    pdf.savefig(fig); plt.close(fig)

                if "journal" in f.columns and not f["journal"].isna().all():
                    jv = f["journal"].value_counts().head(20)
                    fig = plt.figure(figsize=(8.27, 11.69)); ax = fig.add_subplot(111)
                    ax.bar(jv.index.astype(str), jv.values); ax.set_title("Top Journals (Top 20)")
                    ax.set_xticklabels(jv.index.astype(str), rotation=45, ha="right"); ax.set_ylabel("Count"); fig.tight_layout()
                    pdf.savefig(fig); plt.close(fig)

                if "citations_count" in f.columns and f["citations_count"].notna().any():
                    topc = f.sort_values("citations_count", ascending=False).head(20)
                    fig = plt.figure(figsize=(8.27, 11.69)); ax = fig.add_subplot(111); ax.axis('off'); ax.set_title("Top 20 by Citations", pad=20)
                    cols = [c for c in ["title","journal","year","citations_count"] if c in topc.columns]
                    table_data = [cols] + topc[cols].astype(str).values.tolist()
                    table = ax.table(cellText=table_data, loc='center'); table.auto_set_font_size(False); table.set_fontsize(8); table.scale(1,1.2)
                    pdf.savefig(fig); plt.close(fig)
            try:
                with open(pdf_path, "rb") as fh:
                    st.download_button("Download PDF", data=fh.read(), file_name=os.path.basename(pdf_path), mime="application/pdf")
            except Exception as e:
                st.info(f"PDF saved at: {pdf_path}")
                st.error(f"Auto-download failed: {e}")

# -------------------------
# Main Router
# -------------------------
def main():
    st.title(APP_TITLE)
    page = st.sidebar.selectbox("Navigate", ["Data Collection","Quality Assessment","Analysis","Report Generation","Orchestrator Dashboard"])
    if page == "Data Collection":
        render_data_collection()
    elif page == "Quality Assessment":
        render_quality()
    elif page == "Analysis":
        render_analysis()
    elif page == "Report Generation":
        render_report()
    elif page == "Orchestrator Dashboard":
        render_orchestrator_dashboard()

if __name__ == "__main__":
    main()
