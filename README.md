\# Supplier Dependency Risk Score



A screening tool that scores how risky it is to depend on an open-source Python library, using only public GitHub data. It answers one question: which libraries should a company avoid, and what should it do about them?



Six of seven libraries tested scored Low risk. The exception is `python-excel/xlwt`, which scored 9 out of 12 (High). Its owner archived it in May 2020, and it has had no code changes since. The decision memo recommends moving away from it.



The score uses five rules: days since the last push, open issues, number of contributors, days since the last release, and whether the repo is archived. The full thresholds are on the Rules sheet of `data/supplier\_risk.xlsx`.



To run it, set a `GITHUB\_TOKEN` environment variable, then run `py fetch.py` and `py score.py`.



Limits: seven libraries is a small sample. Open issue counts include pull requests, contributors are capped at 100, and the score measures activity, not security or code quality.

