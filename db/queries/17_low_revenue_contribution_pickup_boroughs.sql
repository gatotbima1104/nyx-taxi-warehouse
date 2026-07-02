WITH borough_revenue AS (
    SELECT
        pickup_borough,
        SUM(total_amount) AS total_revenue
    FROM gold.vw_trip_enriched
    GROUP BY pickup_borough
),
borough_summary AS (
    SELECT
        pickup_borough,
        total_revenue,
        total_revenue
            / SUM(total_revenue) OVER () * 100
            AS revenue_contribution_pct
    FROM borough_revenue
)
SELECT
    pickup_borough,
    ROUND(total_revenue, 2) AS total_revenue,
    ROUND(revenue_contribution_pct, 2) AS revenue_contribution_pct,
    CASE
    	WHEN revenue_contribution_pct < 10 THEN 'Less Contribution'
    	WHEN revenue_contribution_pct < 50 THEN 'Normal Contribution'
    	ELSE 'High Contribution'
    END as status_contribution
FROM borough_summary
ORDER BY revenue_contribution_pct DESC;