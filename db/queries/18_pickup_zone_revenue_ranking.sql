WITH total_revenue_by_zone AS (
	SELECT
		ds.pickup_zone,
		SUM(ds.total_amount) AS total_revenue
	FROM gold.vw_trip_enriched AS ds
	GROUP BY 1
	ORDER BY 2 DESC
)
SELECT 
	pickup_zone,
	total_revenue,
	RANK() OVER(
		ORDER BY total_revenue DESC
	) AS ranking
FROM total_revenue_by_zone