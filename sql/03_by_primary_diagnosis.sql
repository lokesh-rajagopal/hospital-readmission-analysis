-- Q3. Readmission rate by primary-diagnosis group (Strack et al. grouping of diag_1).
SELECT diag_group                                     AS grp,
       COUNT(*)                                       AS n,
       SUM(readmit_30)                                AS readmit_30,
       ROUND(100.0 * SUM(readmit_30) / COUNT(*), 2)   AS rate_pct
FROM cohort
GROUP BY diag_group
ORDER BY rate_pct DESC;
