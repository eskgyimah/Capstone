# Capstone — UCC Bibliometric System (Streamlit + Docker)

Unified app with an Orchestrator dashboard: filters, KPIs, charts, exports, DB write-backs (dedupe/materialize/quality), Dry-Run SQL preview, Append/Merge by DOI/PMID, and PDF reports.

## Run Locally (no Docker)

```powershell
py -m pip install --upgrade pip
py -m pip install -r requirements.txt
# Point to your SQLite DB:
$env:BIB_DB="C:\\path\\to\\covid_bibliometric_ucc.db"
py -m streamlit run Capstone.py
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

## Repo bootstrap (Windows, PowerShell)

1. Create a new repo on GitHub under your account: **eskgyimah/Capstone** (public or private). Keep it **empty** (no README, no .gitignore).  
2. Then run:

```powershell
cd "C:\Users\eskgy\Desktop\CAPSTONE\CHATGPT"
mkdir CapstoneRepo
Copy-Item -Path ".\*" -Include Capstone.py, requirements.txt, Dockerfile, .dockerignore, .gitignore -Destination ".\CapstoneRepo" -Force
Copy-Item -Path ".\.streamlit" -Destination ".\CapstoneRepo" -Recurse -Force
Copy-Item -Path ".\.github" -Destination ".\CapstoneRepo" -Recurse -Force

cd CapstoneRepo
git init
git branch -m main
git add .
git -c user.name="Edd" -c user.email="edward.gyimah002@stu.ucc.edu.gh" commit -m "Initial commit: Capstone app + Docker + GH Actions"
git remote add origin https://github.com/eskgyimah/Capstone.git
git push -u origin main
```

After the push, Actions will build and publish `ghcr.io/eskgyimah/capstone:latest`.

## Notes
- Default DB path uses the `BIB_DB` env var; set it when running locally or in Docker.
- The PDF report writes to `reports/` inside the container (non-persistent unless you mount a volume). For persistence: `-v /host/reports:/app/reports`.
- To change the Streamlit theme or port, edit `.streamlit/config.toml` or pass `-e PORT=8501` to Docker.
