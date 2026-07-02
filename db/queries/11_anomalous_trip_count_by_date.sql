WITH daily_trip AS (
	SELECT
		ds.pickup_date,
		COUNT(*) AS total_trips
	FROM gold.vw_trip_enriched AS ds
	WHERE ds.pickup_date >= '2026-01-01' AND ds.pickup_date <= '2026-01-31'
	GROUP BY 1
)
SELECT 
	pickup_date,
	total_trips,
	ROUND(AVG(total_trips) OVER(), 0) AS avg_trips,
	CASE
		WHEN total_trips > AVG(total_trips) OVER() THEN 'Good'
		WHEN total_trips < AVG(total_trips) OVER() * 0.2 THEN 'Bad'
		WHEN total_trips < AVG(total_trips) OVER() * 0.5 THEN 'Very Bad'
		ELSE 'Normal'
	END AS "status"
FROM "daily_trip"