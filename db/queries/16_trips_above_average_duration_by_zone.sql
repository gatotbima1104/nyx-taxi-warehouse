WITH avg_trip_duration_by_zone AS (
	SELECT
		ds.trip_id,
		ds.pickup_zone,
		ds.dropoff_zone,
		ds.trip_duration_minutes,
		ROUND(AVG(ds.trip_duration_minutes) OVER(
			PARTITION BY ds.pickup_zone
		), 2) as avg_trip_duration
	FROM gold.vw_trip_enriched as ds
)
SELECT
	trip_id,
	pickup_zone,
	dropoff_zone,
	trip_duration_minutes,
	avg_trip_duration,
	ROUND((trip_duration_minutes - avg_trip_duration), 2) as total_different_in_minutes,
	CASE
		WHEN trip_duration_minutes < avg_trip_duration THEN 'Under Avg'
		WHEN trip_duration_minutes > avg_trip_duration THEN 'Above Avg'
		ELSE 'On Average'
	END as status
FROM avg_trip_duration_by_zone