CREATE TABLE gold.route_performance_summary AS
SELECT 
	ttc.pickup_zone,
	ttc.dropoff_zone,
	COUNT(*) AS total_trips,
	ROUND(AVG(ttc.total_amount), 2) AS avg_revenue,
	ROUND(SUM(ttc.total_amount), 2) AS total_revenue
FROM silver.taxi_trips_cleaned ttc
GROUP BY 1,2
ORDER BY 5 DESC;