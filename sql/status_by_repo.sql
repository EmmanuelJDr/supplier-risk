SELECT repo,
       CASE
         WHEN archived = 'True' THEN 'Archived'
         WHEN days_since_push > 365 THEN 'Inactive over a year'
         ELSE 'Active'
       END AS status
FROM metrics
ORDER BY status, repo;