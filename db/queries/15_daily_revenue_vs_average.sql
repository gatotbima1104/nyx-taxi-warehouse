WITH daily_revenue AS (
	SELECT 
		ds.pickup_date,
		SUM(ds.total_amount) as total_revenue
	FROM gold.vw_trip_enriched AS ds
	GROUP BY 1
)
SELECT 
	pickup_date,
	total_revenue,
	ROUND(AVG(total_revenue) OVER(), 2) as avg_revenue,
	ROUND(total_revenue - AVG(total_revenue) OVER(), 2) as total_different,
	CASE
		WHEN total_revenue < ROUND(AVG(total_revenue) OVER(), 2) THEN 'Under Avg'
		WHEN total_revenue > ROUND(AVG(total_revenue) OVER(), 2) THEN 'Abover Avg'
		ELSE 'On Average'
	END as status
FROM daily_revenue