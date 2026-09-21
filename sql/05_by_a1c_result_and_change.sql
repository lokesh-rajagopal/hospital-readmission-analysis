-- Q4b. HbA1c result crossed with whether diabetes medication was changed.
SELECT CASE
         WHEN a1c_result = 'None'                  THEN '1. Not tested'
         WHEN a1c_result = 'Norm'                  THEN '2. Normal'
         WHEN a1c_result IN ('>7','>8') AND med_change = 'Ch' THEN '3. High, medication changed'
         ELSE                                           '4. High, medication not changed'
       END                                            AS grp,
       COUNT(*)                                       AS n,
       SUM(readmit_30)                                AS readmit_30,
       ROUND(100.0 * SUM(readmit_30) / COUNT(*), 2)   AS rate_pct
FROM cohort
GROUP BY grp
ORDER BY grp;
