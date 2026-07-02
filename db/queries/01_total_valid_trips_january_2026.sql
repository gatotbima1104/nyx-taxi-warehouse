SELECT
	COUNT(*) AS total_trip
FROM gold.vw_trip_enriched AS ds
WHERE ds.pickup_date >= '2026-01-01' 
    AND ds.pickup_date <= '2026-01-31';