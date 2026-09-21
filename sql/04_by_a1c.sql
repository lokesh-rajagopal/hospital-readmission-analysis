-- Q4a. Was HbA1c measured during the stay? The question the source paper asked.
SELECT CASE a1c_tested WHEN 1 THEN 'HbA1c tested' ELSE 'Not tested' END AS grp,
       COUNT(*)                                       AS n,
       SUM(readmit_30)                                AS readmit_30,
       ROUND(100.0 * SUM(readmit_30) / COUNT(*), 2)   AS rate_pct
FROM cohort
GROUP BY a1c_tested
ORDER BY a1c_tested DESC;
