SELECT
	dqi.error_type,
	COUNT(*)
FROM silver.data_quality_issues dqi 
GROUP BY 1
ORDER BY 2 DESC;