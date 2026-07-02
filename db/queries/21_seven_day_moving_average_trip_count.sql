WITH daily_trips AS (
	SELECT
		ds.pickup_date,
		COUNT(*) as total_trips
	FROM gold.vw_trip_enriched as ds
	GROUP by 1
)
SELECT 
	pickup_date,
	total_trips,
	ROUND(
		AVG(total_trips) OVER (
			ORDER BY pickup_date
			ROWS BETWEEN 6 PRECEDING AND CURRENT ROW
		),2
	) AS moving_avg_7d_days
FROM daily_trips
ORDER BY 1