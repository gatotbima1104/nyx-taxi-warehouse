CREATE TABLE gold.zone_performance_summary AS
SELECT 
	ttc.pickup_zone,
	COUNT(*) AS total_trips,
	ROUND(SUM(ttc.total_amount), 2) AS total_revenue,
	ROUND(AVG(ttc.total_amount), 2) AS avg_revenue
FROM silver.taxi_trips_cleaned ttc
GROUP BY 1
ORDER BY 2 DESC;