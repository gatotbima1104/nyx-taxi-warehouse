BEGIN;

TRUNCATE TABLE silver.taxi_trips_cleaned RESTART IDENTITY;

INSERT INTO silver.taxi_trips_cleaned(
    vendor_id,
    pickup_datetime,
    dropoff_datetime,
    passenger_count,
    trip_distance,
    rate_code_id,
    store_and_fwd_flag,
    pickup_location_id,
    dropoff_location_id,
    payment_type,
    fare_amount,
    -- extra,
    -- mta_tax,
    tip_amount,
    -- tolls_amount,
    -- improvement_surcharge,
    total_amount,
    -- congestion_surcharge,
    -- airport_fee,
    -- cbd_congestion_fee,

    pickup_date,
    pickup_hour,
    pickup_day_time,
    is_weekend,
    time_period,
    trip_duration_minutes,

    pickup_borough,
    pickup_zone,
    dropoff_borough,
    dropoff_zone
)
SELECT
    VendorID,
    tpep_pickup_datetime::TIMESTAMP,
    tpep_dropoff_datetime::TIMESTAMP,
    COALESCE(passenger_count::INTEGER, 0),
    COALESCE(trip_distance::NUMERIC(10,2), -999),
    COALESCE(RatecodeID::INTEGER, -999),
    CASE store_and_fwd_flag
        WHEN 'Y' THEN 'Store and Forward'
        WHEN 'N' THEN 'Normal'
        ELSE 'Unknown'
    END,
    PULocationID,
    DOLocationID,
    CASE payment_type
        WHEN 1 THEN 'Credit Card'
        WHEN 2 THEN 'Cash'
        WHEN 3 THEN 'No Charge'
        WHEN 4 THEN 'Dispute'
        WHEN 0 THEN 'Unknown'
        ELSE 'Unknown'
    END,
    COALESCE(fare_amount, -999),
    -- COALESCE(extra, -999),
    -- COALESCE(mta_tax, -999),
    COALESCE(tip_amount, -999),
    -- COALESCE(tolls_amount, -999),
    -- improvement_surcharge,
    COALESCE(total_amount, -999),
    -- COALESCE(congestion_surcharge, -999),
    -- COALESCE(Airport_fee, -999),
    -- COALESCE(cbd_congestion_fee, -999),

    DATE(tpep_pickup_datetime),
    EXTRACT(HOUR FROM tpep_pickup_datetime)::INTEGER,
    TRIM(TO_CHAR(tpep_pickup_datetime,'Day')),
    CASE 
        WHEN EXTRACT(DOW FROM tpep_pickup_datetime) IN (0,6) THEN TRUE
        ELSE FALSE
    END,
    CASE
        WHEN EXTRACT(HOUR FROM tpep_pickup_datetime) BETWEEN 0 AND 4 THEN 'Late Night'
        WHEN EXTRACT(HOUR FROM tpep_pickup_datetime) BETWEEN 5 AND 11 THEN 'Morning'
        WHEN EXTRACT(HOUR FROM tpep_pickup_datetime) BETWEEN 12 AND 16 THEN 'Afternoon'
        WHEN EXTRACT(HOUR FROM tpep_pickup_datetime) BETWEEN 17 AND 20 THEN 'Evening'
        ELSE 'Night'
    END,
    ROUND(
        (
            EXTRACT(EPOCH FROM (
                tpep_dropoff_datetime - tpep_pickup_datetime
            )) / 60   
        )::NUMERIC,2
    ),
    spu.borough,
    spu.zone,
    sdo.borough,
    sdo.zone
FROM bronze.raw_taxi_trips brt
LEFT JOIN silver.taxi_zones spu
ON brt.PULocationID = spu.location_id
LEFT JOIN silver.taxi_zones sdo
ON brt.DOLocationID = sdo.location_id
WHERE brt.tpep_pickup_datetime < brt.tpep_dropoff_datetime 
    AND brt.trip_distance > 0
    AND brt.passenger_count > 0
    AND brt.fare_amount > 0
    AND brt.tip_amount >= 0
    AND brt.tpep_pickup_datetime >= %(start_period)s
    AND brt.tpep_pickup_datetime < %(end_period)s;

COMMIT;