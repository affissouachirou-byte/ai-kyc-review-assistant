# Portfolio Release Freeze — AI KYC Review Assistant

**Target label:** `v1.0-portfolio` (label only; no release or repository created automatically).

## Freeze on your Windows machine

1. **Stop changing application code** for this portfolio release. In particular, freeze `src/main.py`, `src/prompt_builder.py`, `src/evidence_validator.py` and the rest of `src/` as last tested.
2. **Run final baseline once** from the project root:

   ```powershell
   .\.venv311\Scripts\python.exe -m pytest tests/ -q
   ```

   Record the actual output. Prior reported baseline: **19 passed**.
3. **Archive the source and documentation**, excluding environments, credentials, local logs and generated output. From the project root:

   ```powershell
   Compress-Archive -Path src,tests,data,README.md,requirements.txt,.gitignore,docs -DestinationPath ai-kyc-review-assistant-v1.0-portfolio.zip -Force
   ```

   This archive deliberately omits `evaluation/` and its raw model outputs. Retain evaluation evidence separately and safely; add only approved synthetic evaluation scripts, expectations and summaries to the repository.
4. Copy the supplied `README.md` into the project root after reviewing it; store `EVALUATION_SUMMARY.md` and this checklist inside `docs/`.
5. Before any GitHub publication, manually review files for **API keys, private data, absolute user paths, raw logs, temporary files**. `.gitignore` is not encryption or a substitute for reviewing files.
6. Make the GitHub repository **private initially**, then decide whether to publish a sanitized version. No GitHub repository is created by this checklist.

## Release acceptance criteria

- [ ] `19 passed` (or greater) under Python 3.11 after the freeze
- [ ] No secrets or sensitive records in files selected for publication
- [ ] README installation/run instructions match actual repository contents
- [ ] Original v0.1 evaluation preserved separately
- [ ] EVAL-007 false positive and narrow evaluator coverage documented
- [ ] Human-review flag clearly separated from real human approval
- [ ] Label clearly says **portfolio prototype — not production-ready**

**Do not** delete existing output review files just to make a demo run succeed; the saver intentionally rejects overwrites.
