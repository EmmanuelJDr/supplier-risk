\# Decision Memo: Open-Source Supplier Risk



\*\*Question:\*\* Which open-source libraries should we avoid depending on, and what should we do about them?



\*\*Finding:\*\* Of seven libraries scored, six are Low risk and one is High risk. The High-risk library is python-excel/xlwt. Its owner archived it in May 2020, and it has had no code changes for about 6.7 years.



\*\*Recommendation:\*\*

\- \*\*python-excel/xlwt:\*\* Do not use it in new work. Plan a migration to openpyxl for .xlsx files, and check whether any current code writes .xls files.

\- \*\*The six Low-risk libraries:\*\* No immediate action. Review their scores once a year.



\*\*Limits:\*\* The score uses GitHub activity only. It does not measure security or code quality, and seven libraries is a small sample.

