\# Supplier Dependency Risk Score



\## Business question

Which open-source libraries should a company avoid depending on, and what should it do about them?



\## Data

Public GitHub REST API: repository details, latest release, and contributor count. Collected on 1 November 2026 for seven libraries. Results are cached in the cache folder.



\## Method

Five rules, each awarded points. The maximum is 12, and higher means riskier:



\- Inactivity (days since last push): 0 to 2 points

\- Open issues: 0 to 2 points

\- Maintainer depth (contributors): 0 to 2 points

\- Release recency (days since latest release, or no release): 0 to 3 points

\- Archived by its owner: 3 points



Risk levels: 0 to 3 is Low, 4 to 6 is Medium, 7 or more is High. The full rules are on the Rules sheet of `data/supplier\_risk.xlsx`.



\## Results

\- \*\*Low risk (6 libraries, scores 0 to 2):\*\* psf/requests, pallets/flask, pandas-dev/pandas, jsvine/pdfplumber, microsoft/playwright-python, madmaze/pytesseract.

\- \*\*High risk (1 library, score 9):\*\* python-excel/xlwt. Its owner archived it in May 2020, it has had no push for about 6.7 years, and it has no published GitHub release.



\## Recommendation

\- \*\*python-excel/xlwt:\*\* do not start new work on it. Plan a migration to a maintained library, such as openpyxl for .xlsx output, and check whether any existing code still depends on .xls files.

\- \*\*Low-risk libraries:\*\* no action needed now. Review their scores once a year.



\## Limits

\- Seven libraries is a small sample, chosen to include both active and inactive projects. Treat the scale as a screening tool, not a verdict.

\- Open issue counts on GitHub include pull requests, so they run higher than the Issues tab alone.

\- Contributor counts are capped at 100 per request.

\- The score measures GitHub activity only. It does not measure security or code quality.

\- Cached results are reused until you delete the cache folder.



\## How to run

1\. Set `GITHUB\_TOKEN` as an environment variable.

2\. `py -m pip install openpyxl`

3\. `py fetch.py`

4\. `py score.py`

