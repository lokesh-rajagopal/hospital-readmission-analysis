-- Q10. Fields with any missing values, worst first.
SELECT field, pct_missing
FROM dq_missing
WHERE pct_missing > 0
ORDER BY pct_missing DESC;
