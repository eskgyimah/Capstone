# COVID-19 Bibliometric Analysis Framework

**University of Cape Coast | Department of Data Science and Economic Policy**

A production-ready Streamlit application for academic bibliometric analysis with institutional branding, API integration capabilities, and comprehensive data management tools.

## Features

✅ **Institutional Branding** - UCC logo, student details, professional sidebar
✅ **5 Functional Pages** - Dashboard, Analysis, Data Collection, Quality Assessment, Reports
✅ **API Integration** - PubMed, CrossRef, Europe PMC (UI ready, implementation guide included)
✅ **Data Management** - CSV import, deduplication, schema fixes, quality scoring
✅ **Export Formats** - CSV, RIS, BibTeX, PDF reports
✅ **Database Operations** - Append/merge, deduplicate, quality filtering, dry-run SQL
✅ **Clean Data** - 454 deduplicated records, fixed schema

## Quick Start

```powershell
cd C:\Users\eskgy\Desktop\DMA_CAPSTONE
python -m pip install --upgrade pip
python -m pip install -r requirements.txt
python -m streamlit run Capstone.py
```

Or use the push script:
```powershell
# Double-click: 🦇⬆️.bat (auto-commit and push)
```

## Run with Docker

```powershell
docker build -t capstone:latest .
# mount your DB into /data and point the env var:
docker run -it --rm -p 8501:8501 -e BIB_DB=/data/covid_bibliometric_ucc.db -v "C:\\path\\to\\dbfolder:/data" capstone:latest
```

Open: http://localhost:8501

## GitHub Actions → GHCR

On push to `main`, CI builds and pushes a multi-arch image to **ghcr.io/OWNER/capstone**.

To pull and run:
```bash
docker pull ghcr.io/OWNER/capstone:latest
docker run -it --rm -p 8501:8501 -e BIB_DB=/data/covid_bibliometric_ucc.db -v /abs/path/to/db:/data ghcr.io/OWNER/capstone:latest
```

> Ensure **Packages** visibility in your GitHub user settings allows read access (default OK).

## Project Structure

```
C:\Users\eskgy\Desktop\DMA_CAPSTONE\
├── Capstone.py              # Main Streamlit application
├── UCC_Logo.png             # Institution logo
├── covid_bibliometric_ucc.db # SQLite database (454 deduplicated records)
├── 🦇⬆️.bat                  # Git push automation script
├── deduplicate.py           # Deduplication utility
├── fix_schema.py            # Schema repair tool
├── requirements.txt         # Python dependencies
├── Dockerfile              # Docker configuration
├── .gitignore              # Git ignore rules
├── README.md               # This file
└── reports/                # Generated PDF reports
```

## Documentation

- **BRANDING_COMPLETE.md** - Institutional branding implementation
- **FIXES_SUMMARY.md** - Database schema fixes
- **OPTION_A_APPLIED.md** - Deduplication approach
- **UI_IMPROVEMENTS.md** - UI enhancements

## Git Workflow

Already set up and connected to: **https://github.com/eskgyimah/Capstone.git**

To push changes:
```powershell
# Method 1: Use the automation script
.\🦇⬆️.bat

# Method 2: Manual git commands
git add .
git commit -m "Your message"
git push
```

## API Integration

The Data Collection page includes UI for three major academic APIs:

1. **PubMed API** - Biomedical literature (NCBI)
2. **CrossRef API** - Scholarly publications with DOI
3. **Europe PMC API** - European biomedical database

**Status:** UI ready, implementation guide included in-app

**To implement:**
```bash
pip install biopython requests
```

See in-app documentation (📁 Data Collection → 🔌 API Data Collection) for sample code and integration steps.

## Notes

- Default DB path: `covid_bibliometric_ucc.db` (454 deduplicated records)
- PDF reports saved to `reports/` directory
- All paths use Windows format: `C:\Users\eskgy\Desktop\DMA_CAPSTONE\`
- UCC institutional branding fully integrated

---

## Author

**Edward Solomon Kweku Gyimah**
- Student ID: SE/DAT/24/0007
- Email: edward.gyimah002@stu.ucc.edu.gh
- Programme: MSc Social Science Data Management & Analysis
- Institution: University of Cape Coast
- Department: Data Science and Economic Policy

**Submission:** October 2025

---

**Repository:** https://github.com/eskgyimah/Capstone
