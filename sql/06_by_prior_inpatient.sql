-- Q5. Inpatient admissions in the year before this encounter.
SELECT CASE WHEN number_inpatient >= 3 THEN '3+' ELSE CAST(number_inpatient AS TEXT) END AS grp,
       COUNT(*)                                       AS n,
       SUM(readmit_30)                                AS readmit_30,
       ROUND(100.0 * SUM(readmit_30) / COUNT(*), 2)   AS rate_pct
FROM cohort
GROUP BY grp
ORDER BY grp;
