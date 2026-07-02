SELECT
	SUM(ds.total_amount) AS total_revenue,
	ROUND(AVG(ds.total_amount), 2) AS avg_revenue,
	ROUND(AVG(ds.fare_amount), 2) AS avg_fare
FROM gold.vw_trip_enriched AS ds;