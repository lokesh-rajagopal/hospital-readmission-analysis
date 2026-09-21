-- Q7. Discharge destination, joined to the lookup table. Destinations with < 100 patients folded into 'Other'.
WITH d AS (
    SELECT c.readmit_30, COALESCE(l.description, 'Not recorded') AS dest
    FROM cohort c
    LEFT JOIN lk_discharge_disposition l ON l.id = c.discharge_disposition_id
), sized AS (
    SELECT dest, COUNT(*) AS cnt FROM d GROUP BY dest
)
SELECT CASE WHEN s.cnt >= 100 THEN d.dest ELSE 'Other (< 100 patients each)' END AS grp,
       COUNT(*)                                        AS n,
       SUM(d.readmit_30)                               AS readmit_30,
       ROUND(100.0 * SUM(d.readmit_30) / COUNT(*), 2)  AS rate_pct
FROM d JOIN sized s USING (dest)
GROUP BY grp
ORDER BY n DESC;
