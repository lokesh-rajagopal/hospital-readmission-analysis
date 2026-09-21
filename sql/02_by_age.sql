-- Q2. Readmission rate by age band, in clinical order rather than alphabetical.
SELECT c.age_band                                     AS grp,
       COUNT(*)                                       AS n,
       SUM(c.readmit_30)                              AS readmit_30,
       ROUND(100.0 * SUM(c.readmit_30) / COUNT(*), 2) AS rate_pct
FROM cohort c
JOIN lk_age_band a ON a.age_band = c.age_band
GROUP BY c.age_band
ORDER BY MIN(a.sort_key);
