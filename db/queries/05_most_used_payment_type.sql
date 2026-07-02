SELECT
	ds.payment_type,
	COUNT(*) AS total_trips,
	ROUND(
		COUNT(*) * 100.0 / SUM(COUNT(*)) OVER(), 2
	) AS "percentages"
FROM gold.vw_trip_enriched AS ds
GROUP BY 1
ORDER BY 2 DESC;