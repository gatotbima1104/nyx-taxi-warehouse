SELECT
	ds.pickup_zone ,
	COUNT(*) AS total_trips,
	ROUND(
		COUNT(*) * 100.0 / SUM(COUNT(*)) OVER(), 2
	) AS "percentages",
	SUM(ds.total_amount) AS revenue
FROM gold.vw_trip_enriched AS ds
GROUP BY 1
ORDER BY 3 DESC;