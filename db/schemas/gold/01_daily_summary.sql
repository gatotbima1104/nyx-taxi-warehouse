CREATE TABLE gold.daily_summary AS
SELECT
	ttc.pickup_date,
	COUNT(*) AS total_trips,
	ROUND(SUM(ttc.total_amount), 2) AS daily_revenue,
	ROUND(AVG(ttc.total_amount), 2) AS avg_daily_revenue,
	ROUND(AVG(ttc.trip_distance), 2) AS avg_trip_distance,
	ROUND(AVG(ttc.trip_duration_minutes), 2) AS avg_duration_minute
FROM silver.taxi_trips_cleaned ttc
GROUP BY 1;