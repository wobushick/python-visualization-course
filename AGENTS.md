# AGENTS.md

Compact guidance for future OpenCode sessions in this repository. Keep this file focused on repo-specific facts that are easy to miss.

## Repo shape

- This is a small Python teaching project, not a packaged app: no `pyproject.toml`, `setup.cfg`, `tox.ini`, `pytest.ini`, CI workflow, or build/lint/typecheck config was found.
- Prefer executable sources over prose: read `CLAUDE.md`, `environment.yml`, entrypoint scripts, pytest fixtures, and representative test/dashboard code before inferring behavior.
- Existing local guidance matters: `CLAUDE.md` is more current than older README/docs for the conda environment name and Day3/Day4 behavior.

## Environment and secrets

- Use the conda environment from `environment.yml`: `conda activate data-viz`. Some docs mention `viz-course`; verify locally if a command fails.
- `.env` files are secret and ignored. Day1 and Day3 read DeepSeek config from `test/day1/.env`; do not print, commit, or edit real keys unless explicitly asked.
- Do not tell users to copy `test/day1/.env.example` unless it exists; current repo state has `.env` files but no `.env.example`.

## Commands that matter

```bash
# Day1: generate 20 login test cases from DeepSeek
python test/day1/app.py
# outputs: test/day1/output/testcases.xlsx and test/day1/output/testcases.md

# Day2: run 30 Selenium tests against test/day2/login.html
cd test/day2/selenium
pytest -v
HEADLESS=1 pytest -v

# Focused Day2 runs
pytest -v -k "TestNormalLogin"
pytest -v -k "bob_01"
HEADLESS=1 pytest -v -k "TestSecurity"

# Day3: Gradio all-in-one UI
python test/day3/app.py
# Gradio: http://127.0.0.1:7863
# dashboard static server used for opening dashboard.html: http://localhost:7864/dashboard.html

# Day4: pyecharts dashboard from test results
python test/day4/dashboard.py
# output: test/day4/output/dashboard.html
```

## Architecture facts

- `test/day1/app.py` is the standalone Day1 CLI: DeepSeek/OpenAI-compatible API → Markdown table → Excel via pandas/openpyxl.
- `test/day3/test_case_gen.py` is the reusable generator shared by Day3; model defaults differ from Day1 (`deepseek-chat` default here, `deepseek-v4` in Day1, `deepseek-v4-flash` in the Day3 UI).
- `test/day2/selenium/conftest.py` owns Selenium setup:
  - starts a local HTTP server for `test/day2/` automatically; do not require users to start one manually.
  - supports `APP_URL` override.
  - hardcodes Chrome paths at `~/tools/chrome-linux64/chrome` and `~/tools/chromedriver-linux64/chromedriver`.
  - writes `test/day2/selenium/test_results.json` and failure screenshots under `test/day2/selenium/screenshots/`.
- Day2 Selenium tests use the HTML login page; Day3 manual login reuses `test/day2/login_page.py` validation logic.
- Day3 runs Selenium through `subprocess.run(["pytest", "-v", "--tb=short"], cwd=test/day2/selenium, timeout=300)` and copies results to `test/day3/output/test_results.json`.
- Day4 reads test results from `test/day3/output/test_results.json` first, then falls back to `test/day2/selenium/test_results.json`.
- Day4 builds a `pyecharts.Page` with four charts: input type pie, average duration bar, validation-rule bar, and category × input-type stacked bar.

## Login rules to preserve across changes

- Validation trims username/password first, so leading/trailing spaces become empty-value failures.
- Username: 3-20 chars, only letters/digits/underscore.
- Password: 8-20 chars and must include lowercase, uppercase, and digit.
- SQL/XSS patterns are checked before account matching.
- Valid accounts are hardcoded in both HTML and `login_page.py`: `alice`, `bob_01`, `admin`, `test_user`, `charlie`.

## Testing and artifact gotchas

- Full Day2 can take around 90s; use `-k` for focused verification.
- Generated artifacts are ignored: `output/`, `*.xlsx`, `test/day2/selenium/test_results.json`, and `test/day2/selenium/screenshots/`.
- Changing UI messages can break Day4 chart categorization because `_normalize_output()` maps `actual_output` by keyword.
- Before editing, check `git status`; this repo has local instruction/config files and may have unrelated in-progress changes.
