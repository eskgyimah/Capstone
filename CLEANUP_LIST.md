# Repository Cleanup List

## 🗑️ FILES TO DELETE (Cleanup Recommended)

### 1. Internal Development Files (Not needed on GitHub)
```
.claude/settings.local.json
EMAIL_DETAILS.txt
EMAIL_TO_SUPERVISOR.html
GITHUB_PAGES_DEPLOYMENT.txt
QUICK_START.txt
START_HERE.md
📖_START_HERE_EDWARD.txt
```
**URLs:**
- https://eskgyimah.github.io/Capstone/EMAIL_TO_SUPERVISOR.html

---

### 2. Duplicate/Old Manuscript Versions
```
MANUSCRIPTS/DMA810TS_SE_DAT_24_0007 - Copy.docx
MANUSCRIPTS/DMA810TS_SE_DAT_24_0007_BETA.docx
MANUSCRIPTS/DMA810TS_SE_DAT_24_0007_BETA2.pdf
MANUSCRIPTS/DMA810TS_SE_DAT_24_0007.rar
MANUSCRIPTS/DMA810TS_SE_DAT_24_0007.zip
MANUSCRIPTS/Section 5.6
```

---

### 3. Internal Documentation/Notes (Not Public Facing)
```
MANUSCRIPTS/CAPSTONE_COMPLETION_GUIDE.md
MANUSCRIPTS/HOW_TO_CREATE_FINAL_DOCX.md
MANUSCRIPTS/MISSING_SECTIONS_TO_ADD.md
MANUSCRIPTS/PAGE_BREAKS_TO_ADD.txt
MANUSCRIPTS/FINAL_IMPLEMENTATION_PACKAGE.md
MANUSCRIPTS/FINAL_STRUCTURE_COMPLETE.txt
MANUSCRIPTS/FINAL_UPDATE_COMPLETE.txt
MANUSCRIPTS/README_WORD_READY.txt
```

---

### 4. Email/Submission Files (Local Use Only)
```
MANUSCRIPTS/DMA898 Capstone Project Submission for Review - Edward Gyimah (SEDAT240007).msg
DOCUMENTATION/EMAIL_TO_DR_KOFINTI.html
DOCUMENTATION/.academic_profile.json
```
**URLs:**
- https://eskgyimah.github.io/Capstone/DOCUMENTATION/EMAIL_TO_DR_KOFINTI.html

---

### 5. Utility Scripts (Not Needed)
```
PRESENTATION/create_banner_png.py
PRESENTATION/create_poster_png.py
PRESENTATION/BANNERS_SUMMARY.txt
PRESENTATION/BANNER_README.txt
```

---

### 6. Internal README Files (Redundant)
```
DATA/README.txt
FIGURES/README.txt
PDF/README.txt
PRESENTATION/README.txt
MANUSCRIPTS/README.txt
DOCUMENTATION/README.txt
```
(Keep main README.md only)

---

## ✅ FILES TO KEEP (Essential Academic Materials)

### Core Manuscripts
```
MANUSCRIPTS/DMA810TS_SE_DAT_24_0007.docx        (Main manuscript)
MANUSCRIPTS/DMA810TS_SE_DAT_24_0007.html        (HTML version)
MANUSCRIPTS/DMA810TS_SE_DAT_24_0007.pdf         (PDF version)
MANUSCRIPTS/DMA810TS_SE_DAT_24_0007_REVIEW_SUBMIT.docx  (Submission version)
MANUSCRIPTS/COPY_PASTE_INSTRUCTIONS.html
MANUSCRIPTS/Capstone_HardCopy_Specs.docx.pdf
```

### Presentations & Posters
```
PRESENTATION/CAPSTONE_PRESENTATION_1026.pptx
PRESENTATION/POSTER.html
PRESENTATION/POSTER_A4.html
PRESENTATION/presentation_banner.html
PRESENTATION/presentation_banner_v2_poster.html
PRESENTATION/UCC_Logo.png
```

### Figures (All)
```
FIGURES/Figure1_Comprehensive_Dashboard.png
FIGURES/Figure2_Annual_Publication_Trends.png
FIGURES/Figure3_Quality_Score_Distribution.png
FIGURES/Figure4_Annual_Quality_Evolution.png
FIGURES/Figure5_Top_20_Journals.png
```

### Research Data (All)
```
DATA/citation-*.ris (12 files - keep all)
```

### Public Documentation
```
DOCUMENTATION/MANUSCRIPT_VERSIONS_GUIDE.html
DOCUMENTATION/SUBMISSION_PACKAGE_GUIDE.html
DOCUMENTATION/MY_ACADEMIC_PROFILE.html
DOCUMENTATION/AUTHOR_INFORMATION_FOR_SUBMISSION.html
DOCUMENTATION/COVER_LETTERS_FOR_SUBMISSION.html
DOCUMENTATION/UCC RESEARCH GUIDE.pdf
DOCUMENTATION/COVID19_Technical_Dictionary.dic
DOCUMENTATION/FINAL_PACKAGE_SUMMARY.md
DOCUMENTATION/PACTING_SYSTEM.md
```

### Root Files
```
README.md
index.html
UCC_Logo.png
```

### Other
```
PDF/TERM_PAPER.pdf
```

---

## 📊 Summary

**Files to Delete:** ~35 files
**Files to Keep:** ~40 files
**Space Saved:** Significant (removing .rar, .zip, duplicate .docx files)

---

## 🔧 Cleanup Commands

### Option A: Delete All at Once (Careful!)
```bash
# Review first, then delete
git rm .claude/settings.local.json
git rm EMAIL_DETAILS.txt
git rm EMAIL_TO_SUPERVISOR.html
git rm GITHUB_PAGES_DEPLOYMENT.txt
git rm QUICK_START.txt
git rm START_HERE.md
git rm "📖_START_HERE_EDWARD.txt"
git rm "MANUSCRIPTS/DMA810TS_SE_DAT_24_0007 - Copy.docx"
git rm MANUSCRIPTS/DMA810TS_SE_DAT_24_0007_BETA.docx
git rm MANUSCRIPTS/DMA810TS_SE_DAT_24_0007_BETA2.pdf
git rm MANUSCRIPTS/DMA810TS_SE_DAT_24_0007.rar
git rm MANUSCRIPTS/DMA810TS_SE_DAT_24_0007.zip
git rm "MANUSCRIPTS/Section 5.6"
git rm MANUSCRIPTS/CAPSTONE_COMPLETION_GUIDE.md
git rm MANUSCRIPTS/HOW_TO_CREATE_FINAL_DOCX.md
git rm MANUSCRIPTS/MISSING_SECTIONS_TO_ADD.md
git rm MANUSCRIPTS/PAGE_BREAKS_TO_ADD.txt
git rm MANUSCRIPTS/FINAL_IMPLEMENTATION_PACKAGE.md
git rm MANUSCRIPTS/FINAL_STRUCTURE_COMPLETE.txt
git rm MANUSCRIPTS/FINAL_UPDATE_COMPLETE.txt
git rm MANUSCRIPTS/README_WORD_READY.txt
git rm "MANUSCRIPTS/DMA898 Capstone Project Submission for Review - Edward Gyimah (SEDAT240007).msg"
git rm DOCUMENTATION/EMAIL_TO_DR_KOFINTI.html
git rm DOCUMENTATION/.academic_profile.json
git rm PRESENTATION/create_banner_png.py
git rm PRESENTATION/create_poster_png.py
git rm PRESENTATION/BANNERS_SUMMARY.txt
git rm PRESENTATION/BANNER_README.txt
git rm DATA/README.txt
git rm FIGURES/README.txt
git rm PDF/README.txt
git rm PRESENTATION/README.txt
git rm MANUSCRIPTS/README.txt
git rm DOCUMENTATION/README.txt

# Commit cleanup
git commit -m "Clean repository: Remove internal files, duplicates, and development artifacts"
git push origin main
```

### Option B: Manual Review
Review each file individually before deletion.

---

## ✨ Result: Clean Professional Repository

After cleanup, the repository will contain:
- ✅ Final manuscript versions (DOCX, HTML, PDF)
- ✅ Presentation materials
- ✅ Research data
- ✅ Figures
- ✅ Public-facing documentation
- ✅ Professional README and index

**No more:**
- ❌ Development notes
- ❌ Duplicate files
- ❌ Internal helpers
- ❌ Temporary files
- ❌ Old versions

---

## 🎓 Recommended Action

**Before cleanup:**
1. Download local backup of entire folder
2. Review the deletion list carefully
3. Confirm you don't need any internal notes

**After cleanup:**
- Clean, professional GitHub repository
- Faster clone/download times
- Better organization
- Clear for academic submission
