WITH total_trips_by_zone AS (
	SELECT
		ds.pickup_zone,
		COUNT(*) AS total_trips,
		ROUND(AVG(ds.tip_amount), 2) AS avg_tips
	FROM gold.vw_trip_enriched ds
	GROUP BY 1
	ORDER BY 2 DESC
)
SELECT
	pickup_zone,
	total_trips,
	avg_tips
FROM total_trips_by_zone
ORDER BY 2 DESC, 3
