SELECT repo, stars, open_issues, days_since_push, archived
FROM metrics
WHERE days_since_push > 365 OR archived IN ('True', 'TRUE')
ORDER BY days_since_push DESC;