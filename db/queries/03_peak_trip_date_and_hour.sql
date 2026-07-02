SELECT 
	ds.pickup_date,
	ds.pickup_hour,
	COUNT(*) AS total_trips
FROM gold.vw_trip_enriched AS ds
WHERE ds.pickup_date >= '2026-01-01' AND ds.pickup_date <= '2026-01-31'
GROUP BY 1,2
ORDER BY total_trips DESC;