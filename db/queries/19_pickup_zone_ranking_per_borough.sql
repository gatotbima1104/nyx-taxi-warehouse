WITH total_revenue_by_borough AS (
	SELECT
		ds.pickup_zone,
		ds.pickup_borough,
		SUM(ds.total_amount) AS total_revenue
	FROM gold.vw_trip_enriched AS ds
	GROUP BY 1,2
	ORDER BY 3 DESC
)
SELECT 
	pickup_zone,
	pickup_borough,
	total_revenue,
	RANK() OVER(
		PARTITION BY pickup_borough ORDER BY total_revenue DESC
	) AS ranking
FROM total_revenue_by_borough