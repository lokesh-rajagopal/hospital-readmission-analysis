-- Q8. Insulin status during the stay. medications holds only prescribed drugs, so no row = not prescribed.
SELECT COALESCE(m.status, 'Not prescribed')          AS grp,
       COUNT(*)                                       AS n,
       SUM(c.readmit_30)                              AS readmit_30,
       ROUND(100.0 * SUM(c.readmit_30) / COUNT(*), 2) AS rate_pct
FROM cohort c
LEFT JOIN medications m ON m.encounter_id = c.encounter_id AND m.drug = 'insulin'
GROUP BY grp
ORDER BY n DESC;
