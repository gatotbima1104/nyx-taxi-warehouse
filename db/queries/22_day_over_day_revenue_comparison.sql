WITH daily_trips AS (
	SELECT
		ds.pickup_date,
		COUNT(*) as total_trips,
		SUM(ds.total_amount) as total_revenue
	FROM gold.vw_trip_enriched as ds
	GROUP by 1
)
SELECT 
	pickup_date,
    total_revenue,
    LAG(total_revenue) OVER (
        ORDER BY pickup_date
    ) AS prev_revenue,
    ROUND(
        total_revenue -
        LAG(total_revenue) OVER (
            ORDER BY pickup_date
        ),
        2
    ) AS difference
FROM daily_trips
ORDER BY 1