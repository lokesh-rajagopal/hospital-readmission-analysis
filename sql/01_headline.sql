-- Q1. Overall volumes and the headline 30-day readmission rate.
SELECT
    (SELECT COUNT(*)                    FROM encounters)                   AS total_encounters,
    (SELECT COUNT(DISTINCT patient_nbr) FROM encounters)                   AS unique_patients,
    (SELECT COUNT(*) FROM encounters WHERE excluded_reason IS NOT NULL)    AS excluded_encounters,
    COUNT(*)                                                               AS n,
    SUM(readmit_30)                                                        AS readmit_30,
    ROUND(100.0 * SUM(readmit_30) / COUNT(*), 2)                           AS rate_pct,
    ROUND(AVG(time_in_hospital), 2)                                        AS avg_los_days
FROM cohort;
