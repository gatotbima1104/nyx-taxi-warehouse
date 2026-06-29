CREATE TABLE gold.payment_behavior_summary AS
SELECT
	ttc.payment_type,
	COUNT(*) AS total_trips,
    ROUND(COUNT(*) * 100.0 / SUM(COUNT(*)) OVER (), 2) AS trip_percentage,
	ROUND(SUM(ttc.total_amount), 2) AS daily_revenue,
	ROUND(AVG(ttc.total_amount), 2) AS avg_daily_revenue,
	ROUND(AVG(ttc.trip_distance), 2) AS avg_trip_distance,
	ROUND(AVG(ttc.trip_duration_minutes), 2) AS avg_duration_minute,
	ROUND(AVG(ttc.tip_amount), 2) AS avg_tip_amount
FROM silver.taxi_trips_cleaned ttc
GROUP BY 1
ORDER BY 3 DESC;