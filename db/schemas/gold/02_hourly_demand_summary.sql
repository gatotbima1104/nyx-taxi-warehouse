CREATE TABLE gold.hourly_demand_summary AS
SELECT
	ttc.pickup_hour,
	COUNT(*) AS total_trips,
	DENSE_RANK() OVER(
		ORDER BY COUNT(*)
	) AS ranking_demand_hour
FROM silver.taxi_trips_cleaned ttc
GROUP BY 1
ORDER BY ranking_demand_hour;