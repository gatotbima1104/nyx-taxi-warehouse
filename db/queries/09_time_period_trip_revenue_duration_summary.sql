SELECT
	ds.time_period,
	COUNT(*) AS total_trips,
	SUM(ds.total_amount) AS total_revenue,
	ROUND(AVG(ds.total_amount), 2) AS avg_revenue,
	ROUND(AVG(ds.trip_duration_minutes), 2) AS avg_duration
FROM gold.vw_trip_enriched AS ds
GROUP BY 1
ORDER BY 2 DESC,3 DESC;