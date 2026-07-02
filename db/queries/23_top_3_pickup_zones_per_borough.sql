WITH total_revenue_by_borough AS (
	SELECT
		ds.pickup_zone,
		ds.pickup_borough,
		SUM(ds.total_amount) AS total_revenue
	FROM gold.vw_trip_enriched AS ds
	GROUP BY 1,2
	ORDER BY 3 DESC
),
ranking_by_zone AS (
	SELECT 
		pickup_zone,
		pickup_borough,
		total_revenue,
		DENSE_RANK() OVER(
			PARTITION BY pickup_borough 
			ORDER BY total_revenue DESC
		) AS "ranking"
	FROM total_revenue_by_borough
)
SELECT 
*
FROM ranking_by_zone
WHERE ranking < 4