WITH total_revenue_by_date AS (
	SELECT
		ds.pickup_date,
		ds.pickup_zone,
		ds.pickup_borough,
		COUNT(*) AS total_trips,
		SUM(ds.total_amount) AS total_revenue
	FROM gold.vw_trip_enriched AS ds
	GROUP BY 1,2,3
	ORDER BY 3 DESC
)
SELECT 
	pickup_date,
	pickup_zone,
	pickup_borough,
	total_trips,
	total_revenue,
	RANK() OVER(
		ORDER BY total_revenue DESC
	) AS ranking
FROM total_revenue_by_date