--1
SELECT
	COUNT(*) AS total_trip
FROM gold.vw_trip_enriched AS ds
WHERE ds.pickup_date >= '2026-01-01' AND ds.pickup_date <= '2026-01-31';

--2
SELECT
	SUM(ds.total_amount) AS total_revenue,
	ROUND(AVG(ds.total_amount), 2) AS avg_revenue,
	ROUND(AVG(ds.fare_amount), 2) AS avg_fare
FROM gold.vw_trip_enriched AS ds;

--3
SELECT 
	ds.pickup_date,
	ds.pickup_hour,
	COUNT(*) AS total_trips
FROM gold.vw_trip_enriched AS ds
WHERE ds.pickup_date >= '2026-01-01' AND ds.pickup_date <= '2026-01-31'
GROUP BY 1,2
ORDER BY total_trips DESC;

--4
SELECT
	CASE 
		WHEN ds.is_weekend THEN 'Weekend'
		ELSE 'Weekday'
	END AS "day_type",
	COUNT(*) AS total_trips,
	ROUND(
		COUNT(*) * 100.0 / SUM(COUNT(*)) OVER(), 2
	) AS "percentages"
FROM gold.vw_trip_enriched AS ds
GROUP BY 1
ORDER BY 2 DESC;

--5 
SELECT
	ds.payment_type,
	COUNT(*) AS total_trips,
	ROUND(
		COUNT(*) * 100.0 / SUM(COUNT(*)) OVER(), 2
	) AS "percentages"
FROM gold.vw_trip_enriched AS ds
GROUP BY 1
ORDER BY 2 DESC;

--6 
SELECT
	ds.pickup_zone,
	ds.pickup_borough,
	COUNT(*) AS total_trips,
	ROUND(
		COUNT(*) * 100.0 / SUM(COUNT(*)) OVER(), 2
	) AS "percentages"
FROM gold.vw_trip_enriched AS ds
GROUP BY 1,2
ORDER BY 3 DESC;

--7
SELECT
	ds.pickup_zone ,
	COUNT(*) AS total_trips,
	ROUND(
		COUNT(*) * 100.0 / SUM(COUNT(*)) OVER(), 2
	) AS "percentages",
	SUM(ds.total_amount) AS revenue
FROM gold.vw_trip_enriched AS ds
GROUP BY 1
ORDER BY 3 DESC;

--8
SELECT
	ds.pickup_zone,
	ds.pickup_borough,
	ds.dropoff_zone,
	ds.dropoff_borough,
	COUNT(*) as total_trips
FROM gold.vw_trip_enriched AS ds
GROUP BY 1,2,3,4
ORDER BY 5 DESC

--9
SELECT
	ds.time_period,
	COUNT(*) AS total_trips,
	SUM(ds.total_amount) AS total_revenue,
	ROUND(AVG(ds.total_amount), 2) AS avg_revenue,
	ROUND(AVG(ds.trip_duration_minutes), 2) AS avg_duration
FROM gold.vw_trip_enriched AS ds
GROUP BY 1
ORDER BY 2 DESC,3 DESC;

--10
SELECT
	dqi.error_type,
	COUNT(*)
FROM silver.data_quality_issues dqi 
GROUP BY 1
ORDER BY 2 DESC;


--11
WITH daily_trip AS (
	SELECT
		ds.pickup_date,
		COUNT(*) AS total_trips
	FROM gold.vw_trip_enriched AS ds
	WHERE ds.pickup_date >= '2026-01-01' AND ds.pickup_date <= '2026-01-31'
	GROUP BY 1
)
SELECT 
	pickup_date,
	total_trips,
	ROUND(AVG(total_trips) OVER(), 0) AS avg_trips,
	CASE
		WHEN total_trips > AVG(total_trips) OVER() THEN 'Good'
		WHEN total_trips < AVG(total_trips) OVER() * 0.2 THEN 'Bad'
		WHEN total_trips < AVG(total_trips) OVER() * 0.5 THEN 'Very Bad'
		ELSE 'Normal'
	END AS "status"
FROM "daily_trip"

--12 
--Error

--13
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
LIMIT 10;

--14
WITH total_trips_by_zone AS (
	SELECT
		ds.pickup_zone,
		COUNT(*)g AS total_trips,
		ROUND(AVG(ds.tip_amount), 2) AS avg_tips
	FROM gold.vw_trip_enriched ds
	GROUP BY 1
	ORDER BY 2 DESC
)
SELECT
	pickup_zone,
	total_trips,
	avg_tips
FROM total_trips_by_zone
ORDER BY 2 DESC, 3

--15
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

--16
WITH avg_trip_duration_by_zone AS (
	SELECT
		ds.trip_id,
		ds.pickup_zone,
		ds.dropoff_zone,
		ds.trip_duration_minutes,
		ROUND(AVG(ds.trip_duration_minutes) OVER(
			PARTITION BY ds.pickup_zone
		), 2) as avg_trip_duration
	FROM gold.vw_trip_enriched as ds
)
SELECT
	trip_id,
	pickup_zone,
	dropoff_zone,
	trip_duration_minutes,
	avg_trip_duration,
	ROUND((trip_duration_minutes - avg_trip_duration), 2) as total_different_in_minutes,
	CASE
		WHEN trip_duration_minutes < avg_trip_duration THEN 'Under Avg'
		WHEN trip_duration_minutes > avg_trip_duration THEN 'Above Avg'
		ELSE 'On Average'
	END as status
FROM avg_trip_duration_by_zone

--17
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

--18
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


--19
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

--20
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

--21
WITH daily_trips AS (
	SELECT
		ds.pickup_date,
		COUNT(*) as total_trips
	FROM gold.vw_trip_enriched as ds
	GROUP by 1
)
SELECT 
	pickup_date,
	total_trips,
	ROUND(
		AVG(total_trips) OVER (
			ORDER BY pickup_date
			ROWS BETWEEN 6 PRECEDING AND CURRENT ROW
		),2
	) AS moving_avg_7d_days
FROM daily_trips
ORDER BY 1

--22
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


--23
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