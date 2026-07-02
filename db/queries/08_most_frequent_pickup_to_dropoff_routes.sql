SELECT
	ds.pickup_zone,
	ds.pickup_borough,
	ds.dropoff_zone,
	ds.dropoff_borough,
	COUNT(*) as total_trips
FROM gold.vw_trip_enriched AS ds
GROUP BY 1,2,3,4
ORDER BY 5 DESC