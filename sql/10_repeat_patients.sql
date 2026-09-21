-- Q9. How concentrated is utilisation? Uses all non-excluded encounters, not just index ones.
WITH per_patient AS (
    SELECT patient_nbr, COUNT(*) AS encounters
    FROM encounters
    WHERE excluded_reason IS NULL
    GROUP BY patient_nbr
), banded AS (
    SELECT CASE WHEN encounters = 1 THEN '1 encounter'
                WHEN encounters = 2 THEN '2 encounters'
                WHEN encounters <= 4 THEN '3-4 encounters'
                ELSE '5+ encounters' END AS band,
           encounters
    FROM per_patient
)
SELECT band                                                         AS grp,
       COUNT(*)                                                     AS patients,
       SUM(encounters)                                              AS encounters,
       ROUND(100.0 * COUNT(*) / SUM(COUNT(*)) OVER (), 2)           AS pct_of_patients,
       ROUND(100.0 * SUM(encounters) / SUM(SUM(encounters)) OVER (), 2) AS pct_of_encounters
FROM banded
GROUP BY band
ORDER BY band;
