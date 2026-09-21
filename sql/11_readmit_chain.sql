-- Q9b. Window functions: for patients with more than one encounter, is a <30 readmission
-- on one stay followed by another on the next? LAG pulls the previous stay's outcome.
WITH seq AS (
    SELECT patient_nbr,
           encounter_seq,
           readmit_30,
           LAG(readmit_30) OVER (PARTITION BY patient_nbr ORDER BY encounter_id) AS prev_readmit_30
    FROM encounters
    WHERE excluded_reason IS NULL
)
SELECT CASE prev_readmit_30 WHEN 1 THEN 'Previous stay readmitted <30d'
                            ELSE 'Previous stay not readmitted <30d' END AS grp,
       COUNT(*)                                       AS n,
       SUM(readmit_30)                                AS readmit_30,
       ROUND(100.0 * SUM(readmit_30) / COUNT(*), 2)   AS rate_pct
FROM seq
WHERE prev_readmit_30 IS NOT NULL
GROUP BY grp
ORDER BY grp DESC;
