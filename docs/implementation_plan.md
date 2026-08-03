# Implementation Plan - AI JobAgent Enhancements & Fixes

This plan outlines the design and implementation steps for resolving the 13 reported issues and implementing requested improvements, including location fallback logic, contact extraction (Kaggle/LeetCode/HackerRank), skill-quality scoring, scanned/two-column PDF parsing, base provider class refactoring, new providers (JSearch, TheMuse, Adzuna, Jooble), auto-learning recommendation logic, and an AI Resume Optimizer.

---

## Proposed Changes

### 1. Configuration & Loading Settings (`config.py`)
#### [MODIFY] [config.py](file:///c:/JobAgent/config.py)
- Load `.env` environment variables using `python-dotenv`.
- Add JSearch, Adzuna, TheMuse, and Jooble enablement settings and credentials/endpoints.
- Update `MATCH_WEIGHTS` to:
  ```python
  MATCH_WEIGHTS = {
      "role": 35,
      "skills": 35,
      "experience": 15,
      "location": 10,
      "salary": 5,
  }
  ```

---

### 2. Models Extensions (`models/`)
#### [MODIFY] [resume.py](file:///c:/JobAgent/models/resume.py)
- Add Kaggle, LeetCode, and HackerRank string fields (`kaggle`, `leetcode`, `hackerrank`) to `ResumeData`.
- Update `to_dict` and `from_dict` methods to serialize and deserialize these new fields.

#### [MODIFY] [job.py](file:///c:/JobAgent/models/job.py)
- Add `get_match_reason(self) -> str` helper method to `JobData` showing matched and missing skills (e.g. `Python ✔ | SQL ✔ | Missing: Azure`).

#### [MODIFY] [search.py](file:///c:/JobAgent/models/search.py)
- Add `failed_providers: List[str]` and `learning_path: List[Dict[str, Any]]` fields.
- Update serialization and deserialization helpers.

---

### 3. Core Domain Services (`services/`)
#### [MODIFY] [resume_parser.py](file:///c:/JobAgent/services/resume_parser.py)
- In `extract_pdf()`, update the PyMuPDF parsing to handle 2-column layouts by sorting text blocks horizontally (left-to-right columns) and vertically (top-to-bottom).
- Add check/warning fallback for scanned PDFs (e.g., text content length < 50 characters).

#### [MODIFY] [contact_extractor.py](file:///c:/JobAgent/services/contact_extractor.py)
- Add detection patterns and functions for Kaggle, LeetCode, and HackerRank URLs.

#### [MODIFY] [resume_enricher.py](file:///c:/JobAgent/services/resume_enricher.py)
- Fix the `DEFAULT_PREFERRED_LOCATIONS` NameError by importing and using `DEFAULT_LOCATIONS` from `config.py`.
- Improve `infer_location` to scan career objective/profile summary fields for target city preferences from `DEFAULT_LOCATIONS` before falling back to Bangalore/Bengaluru (instead of using the hometown).
- Add extraction helper functions for Kaggle, LeetCode, and HackerRank.

#### [MODIFY] [resume_analyzer.py](file:///c:/JobAgent/services/resume_analyzer.py)
- In `build_resume_data()`, import and execute extraction for Kaggle, LeetCode, and HackerRank.

#### [MODIFY] [ats_calculator.py](file:///c:/JobAgent/services/ats_calculator.py)
- Refactor `skills_score()` to reward skill quality:
  - Establish a set of high-value industry skills (Python, SQL, Power BI, Tableau, Pandas, Git, FastAPI, Azure, Docker, etc.).
  - Award base points for quantity and bonus points for high-value/core industry skill matches.

#### [MODIFY] [search_jobs.py](file:///c:/JobAgent/services/search_jobs.py)
- Update `fetch_jobs()` to return both matched `JobData` objects and a list of `failed_providers`.
- In `search_jobs()`, filter by location using `resume.preferred_location`. If it's empty, fallback to `resume.location`.
- Count missing skill frequencies across all matched jobs and generate the sorted `learning_path` recommendations (Auto-Learning).

#### [NEW] [resume_optimizer.py](file:///c:/JobAgent/services/resume_optimizer.py)
- Implement `optimize_resume(resume_text, target_role)` querying Ollama to:
  - Rewrite/improve the resume summary.
  - Suggest stronger action verbs and rewrite bullet points.
  - Recommend missing key skills to learn based on the target role.

---

### 4. Providers Layer (`providers/`)
#### [NEW] [base.py](file:///c:/JobAgent/providers/base.py)
- Create `BaseProvider` class standardizing request handling, exception catching, headers, timeouts, and role keyword filtering.

#### [MODIFY] [remotive.py](file:///c:/JobAgent/providers/remotive.py)
- Inherit from `BaseProvider`, reducing codebase length and eliminating duplicate parsing code.

#### [MODIFY] [remoteok.py](file:///c:/JobAgent/providers/remoteok.py)
- Inherit from `BaseProvider`, reducing codebase length and eliminating duplicate parsing code.

#### [MODIFY] [arbeitnow.py](file:///c:/JobAgent/providers/arbeitnow.py)
- Inherit from `BaseProvider`, reducing codebase length and eliminating duplicate parsing code.

#### [NEW] [jsearch.py](file:///c:/JobAgent/providers/jsearch.py)
- Implement RapidAPI JSearch provider utilizing the key from `.env`.

#### [NEW] [themuse.py](file:///c:/JobAgent/providers/themuse.py)
- Implement TheMuse job search provider utilizing their public endpoint.

#### [NEW] [adzuna.py](file:///c:/JobAgent/providers/adzuna.py)
- Implement Adzuna job search provider utilizing keys from `.env`.

#### [NEW] [jooble.py](file:///c:/JobAgent/providers/jooble.py)
- Implement Jooble job search provider utilizing keys from `.env`.

---

### 5. API Entrypoint (`app.py`)
#### [MODIFY] [app.py](file:///c:/JobAgent/app.py)
- Add the `POST /optimize-resume` endpoint invoking the new `resume_optimizer` service.
- Return the new `SearchResult` fields (`failed_providers`, `learning_path`) in `/search-jobs` and `/search-statistics`.

---

## Verification Plan

### Automated Tests
- Build verification script in `scratch/test_enhancements.py` to test:
  1. Resume parser sorting blocks on a multi-column PDF.
  2. Contact extractor parsing Kaggle, LeetCode, and HackerRank links.
  3. Skill scoring rewarding high-quality skills.
  4. Location logic checking `preferred_location` fallback to `location`.
  5. Search job service retrieving from new providers (JSearch/TheMuse) and returning `learning_path` & `failed_providers`.
  6. Resume optimizer calling Ollama API successfully.

- Run verification command:
  ```powershell
  python test_enhancements.py
  ```

### Manual Verification
- Test all REST endpoints using FastAPI docs (`http://127.0.0.1:8000/docs`).
