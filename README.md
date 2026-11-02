# Supplier Dependency Risk Score

A screening tool that scores how risky it is to depend on an open-source Python library, using only public GitHub data. It answers one question: which libraries should a company avoid, and what should it do about them?

I scored 17 widely used libraries. Thirteen are Low risk, three are Medium, and one is High. The High-risk library is `python-excel/xlwt`, which scored 9 out of 12. Its owner archived it in May 2020, it has had no code changes since, and it has no GitHub releases. The decision memo recommends moving away from it.

The score uses five rules: days since the last push, open issues, number of contributors, days since the last GitHub release, and whether the repo is archived. The full thresholds are on the Rules sheet of `data/supplier_risk.xlsx`.

## Known limitation

The release rule only counts GitHub Releases. Projects that publish versions as tags get penalised for having no release. `django/Django` scored Medium because of this, and it is actively maintained, so that result is a false positive. `python-excel/xlrd` also receives the 3-point release penalty but stays Low because it is recently active. I kept the rule unchanged rather than adjust it after seeing the results. A future version should count tags as releases.

Other Medium results are accurate: `psf/requests-html` has not been updated for about 2.5 years and its last release was about 7.7 years ago, and `nose-devs/nose` has been inactive for about 3 years.

To run it, set a `GITHUB_TOKEN` environment variable, then run `py fetch.py` and `py score.py`.

Limits: open issue counts include pull requests, contributors are capped at 100, and the score measures activity, not security or code quality.