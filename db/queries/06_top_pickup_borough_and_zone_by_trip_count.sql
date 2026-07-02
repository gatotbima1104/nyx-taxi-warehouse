SELECT
	ds.pickup_zone,
	ds.pickup_borough,
	COUNT(*) AS total_trips,
	ROUND(
		COUNT(*) * 100.0 / SUM(COUNT(*)) OVER(), 2
	) AS "percentages"
FROM gold.vw_trip_enriched AS ds
GROUP BY 1,2
ORDER BY 3 DESC;