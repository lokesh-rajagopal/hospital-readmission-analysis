-- Q1b. Why the unit of analysis matters: the same outcome counted per encounter vs per patient.
-- no-test: these rows are overlapping populations, so a chi-square test would be invalid.
SELECT 'All encounters (raw)'                        AS grp,
       COUNT(*) AS n, SUM(readmit_30) AS readmit_30,
       ROUND(100.0 * SUM(readmit_30) / COUNT(*), 2)  AS rate_pct
FROM encounters
UNION ALL
SELECT 'All encounters, exclusions removed',
       COUNT(*), SUM(readmit_30), ROUND(100.0 * SUM(readmit_30) / COUNT(*), 2)
FROM encounters WHERE excluded_reason IS NULL
UNION ALL
SELECT 'First encounter per patient (primary cohort)',
       COUNT(*), SUM(readmit_30), ROUND(100.0 * SUM(readmit_30) / COUNT(*), 2)
FROM cohort;
