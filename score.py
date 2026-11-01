"""Score each library's supplier risk and write an Excel workbook."""
import csv
import sys
from pathlib import Path

from openpyxl import Workbook
from openpyxl.chart import BarChart, Reference
from openpyxl.styles import Alignment, Font, PatternFill

IN_FILE = Path("data/metrics.csv")
OUT_FILE = Path("data/supplier_risk.xlsx")

HEADERS = [
    "Repository", "Stars", "Open issues", "Days since last push",
    "Contributors", "Days since release", "Archived",
    "Inactivity pts", "Open issues pts", "Maintainer pts",
    "Release pts", "Archived pts", "Total score", "Risk level",
    "Recommendation",
]

RULES = [
    "How the score works (maximum 12 points; higher means riskier)",
    "",
    "Inactivity: days since last push. 0-180 = 0 pts; 181-365 = 1 pt; over 365 = 2 pts.",
    "Open issues: 0-99 = 0 pts; 100-500 = 1 pt; over 500 = 2 pts.",
    "Maintainer depth: 20+ contributors = 0 pts; 5-19 = 1 pt; under 5 = 2 pts.",
    "Release recency: release in the last 365 days = 0 pts; older = 2 pts; none = 3 pts.",
    "Archived: archived repository = 3 pts; otherwise 0.",
    "",
    "Risk level: 0-3 = Low; 4-6 = Medium; 7 or more = High.",
    "",
    "Limits: open issue counts include pull requests. Contributors are capped at 100.",
    "The score is a screening signal, not proof of security or quality.",
]


def points(row):
    """Return the points for each rule, using the rules listed above."""
    pts = {}
    push = row["days_since_push"]
    if push == "":
        pts["inactivity"] = 2
    else:
        days = int(push)
        pts["inactivity"] = 0 if days <= 180 else 1 if days <= 365 else 2
    issues = int(row["open_issues"])
    pts["issues"] = 0 if issues < 100 else 1 if issues <= 500 else 2
    people = int(row["contributors"])
    pts["maintainers"] = 0 if people >= 20 else 1 if people >= 5 else 2
    release = row["days_since_release"]
    if release == "":
        pts["release"] = 3
    else:
        pts["release"] = 0 if int(release) <= 365 else 2
    pts["archived"] = 3 if row["archived"] == "True" else 0
    return pts


def level_for(total):
    return "Low" if total <= 3 else "Medium" if total <= 6 else "High"


def build_scores_sheet(wb, rows):
    ws = wb.active
    ws.title = "Scores"
    ws.append(HEADERS)
    for i, row in enumerate(rows, start=2):
        pts = points(row)
        ws.append([
            row["repo"],
            int(row["stars"]),
            int(row["open_issues"]),
            int(row["days_since_push"]) if row["days_since_push"] else "n/a",
            int(row["contributors"]),
            int(row["days_since_release"]) if row["days_since_release"] else "n/a",
            row["archived"] == "True",
            pts["inactivity"],
            pts["issues"],
            pts["maintainers"],
            pts["release"],
            pts["archived"],
            f"=SUM(H{i}:L{i})",
            f'=IF(M{i}<=3,"Low",IF(M{i}<=6,"Medium","High"))',
            f'=IF(N{i}="High","Plan a replacement or add monitoring",'
            f'IF(N{i}="Medium","Monitor quarterly","Safe to depend on; review yearly"))',
        ])
    for cell in ws[1]:
        cell.font = Font(bold=True, color="FFFFFF")
        cell.fill = PatternFill("solid", fgColor="1F3864")
        cell.alignment = Alignment(wrap_text=True, vertical="center")
    ws.freeze_panes = "B2"
    widths = [30, 9, 12, 14, 13, 14, 10, 13, 14, 15, 12, 13, 12, 12, 42]
    for idx, width in enumerate(widths, start=1):
        ws.column_dimensions[chr(64 + idx)].width = width


def build_summary_sheet(wb, last_row):
    ws = wb.create_sheet("Summary")
    ws.append(["Risk level", "Libraries"])
    for level in ("Low", "Medium", "High"):
        ws.append([level, f'=COUNTIF(Scores!N2:N{last_row},"{level}")'])
    for cell in ws[1]:
        cell.font = Font(bold=True)
    chart = BarChart()
    chart.title = "Libraries by supplier risk level"
    chart.x_axis.title = "Risk level"
    chart.y_axis.title = "Libraries"
    chart.add_data(Reference(ws, min_col=2, min_row=1, max_row=4),
                   titles_from_data=True)
    chart.set_categories(Reference(ws, min_col=1, min_row=2, max_row=4))
    chart.height, chart.width = 8, 14
    ws.add_chart(chart, "D2")
    ws.column_dimensions["A"].width = 14
    ws.column_dimensions["B"].width = 12


def build_rules_sheet(wb):
    ws = wb.create_sheet("Rules")
    for line in RULES:
        ws.append([line])
    ws["A1"].font = Font(bold=True, size=12)
    ws.column_dimensions["A"].width = 100


def main():
    if not IN_FILE.exists():
        print("data/metrics.csv not found. Run fetch.py first.")
        sys.exit(1)
    with IN_FILE.open(encoding="utf-8") as f:
        rows = list(csv.DictReader(f))
    if not rows:
        print("metrics.csv has no rows. Check repos.txt and run fetch.py again.")
        sys.exit(1)

    wb = Workbook()
    build_scores_sheet(wb, rows)
    build_summary_sheet(wb, last_row=len(rows) + 1)
    build_rules_sheet(wb)
    OUT_FILE.parent.mkdir(exist_ok=True)
    wb.save(OUT_FILE)

    print(f"Saved {OUT_FILE}")
    for row in rows:
        total = sum(points(row).values())
        print(f"{row['repo']:<28} score={total:>2}  level={level_for(total)}")


if __name__ == "__main__":
    main()
