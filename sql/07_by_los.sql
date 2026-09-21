-- Q6. Length of stay, bucketed.
SELECT CASE
         WHEN time_in_hospital <= 2  THEN '1. 1-2 days'
         WHEN time_in_hospital <= 4  THEN '2. 3-4 days'
         WHEN time_in_hospital <= 7  THEN '3. 5-7 days'
         ELSE                             '4. 8-14 days'
       END                                            AS grp,
       COUNT(*)                                       AS n,
       SUM(readmit_30)                                AS readmit_30,
       ROUND(100.0 * SUM(readmit_30) / COUNT(*), 2)   AS rate_pct
FROM cohort
GROUP BY grp
ORDER BY grp;
