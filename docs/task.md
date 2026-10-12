# JobAgent Improvement Tasks

- `[x]` Task 1: Update `config.py` with environment variable loading, new settings, and new match weights.
- `[x]` Task 2: Update `models/resume.py`, `models/job.py`, and `models/search.py` with the new fields and helpers.
- `[x]` Task 3: Update `services/contact_extractor.py` and `services/resume_enricher.py` with Kaggle/LeetCode/HackerRank extraction patterns and fix `infer_location` NameError and logic.
- `[x]` Task 4: Update `services/resume_parser.py` with column-sorting and scanned PDF checks.
- `[x]` Task 5: Update `services/resume_analyzer.py` to extract new profile links.
- `[x]` Task 6: Refactor `services/ats_calculator.py` to reward skill quality.
- `[x]` Task 7: Implement `providers/base.py` (`BaseProvider`) and refactor `remotive.py`, `remoteok.py`, `arbeitnow.py`.
- `[x]` Task 8: Implement new providers: `jsearch.py`, `themuse.py`, `adzuna.py`, `jooble.py`.
- `[x]` Task 9: Update `services/search_jobs.py` with new location filtering, provider tracking, and learning path logic.
- `[x]` Task 10: Create the new service `services/resume_optimizer.py`.
- `[x]` Task 11: Modify `app.py` with the new endpoints and return fields.
- `[x]` Task 12: Build verification script `scratch/test_enhancements.py` and run tests.
