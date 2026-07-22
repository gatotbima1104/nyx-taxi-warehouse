DROP TABLE IF EXISTS silver.data_quality_issues CASCADE;
DROP TABLE IF EXISTS silver.taxi_trips_cleaned CASCADE;
DROP TABLE IF EXISTS silver.taxi_zones CASCADE;

CREATE TABLE silver.taxi_zones(
    location_id INTEGER PRIMARY KEY,
    borough TEXT NOT NULL,
    zone TEXT NOT NULL,
    service_zone TEXT NOT NULL
);

CREATE TABLE silver.taxi_trips_cleaned (
    trip_id BIGSERIAL PRIMARY KEY,
    vendor_id INTEGER NOT NULL,

    pickup_datetime TIMESTAMP NOT NULL,
    pickup_date DATE NOT NULL,
    pickup_hour INTEGER NOT NULL,
    pickup_day_time TEXT NOT NULL,
    is_weekend BOOLEAN NOT NULL,
    time_period TEXT NOT NULL CHECK (time_period IN ('Late Night', 'Morning', 'Afternoon', 'Evening', 'Night')),
    pickup_borough TEXT NOT NULL,
    pickup_zone TEXT NOT NULL,

    dropoff_datetime TIMESTAMP NOT NULL,
    dropoff_borough TEXT NOT NULL,
    dropoff_zone TEXT NOT NULL,

    passenger_count INTEGER NOT NULL CHECK (passenger_count > 0),

    trip_distance NUMERIC(10,2) NOT NULL CHECK (trip_distance > 0),
    trip_duration_minutes NUMERIC(10,2) NOT NULL CHECK (trip_duration_minutes > 0),

    rate_code_id INTEGER NOT NULL,
    store_and_fwd_flag TEXT NOT NULL CHECK (store_and_fwd_flag IN ('Normal', 'Store and Forward', 'Unknown')),
    pickup_location_id INTEGER NOT NULL,
    dropoff_location_id INTEGER NOT NULL,
    payment_type TEXT NOT NULL CHECK (payment_type IN ('Credit Card', 'Cash', 'No Charge', 'Dispute', 'Unknown')),
    
    fare_amount NUMERIC(10,2) NOT NULL CHECK (fare_amount > 0),
    tip_amount NUMERIC(10,2) NOT NULL CHECK (tip_amount >= 0),
    total_amount NUMERIC(10,2) NOT NULL CHECK (total_amount > 0),

    CONSTRAINT fk_pickup
        FOREIGN KEY(pickup_location_id) 
        REFERENCES silver.taxi_zones(location_id),

    CONSTRAINT fk_dropoff
        FOREIGN KEY(dropoff_location_id) 
        REFERENCES silver.taxi_zones(location_id),

    CONSTRAINT chk_pickup_hour CHECK (pickup_hour BETWEEN 0 AND 23),
    CONSTRAINT chk_pickup_before_dropoff CHECK(pickup_datetime < dropoff_datetime)

);

CREATE TABLE silver.data_quality_issues (
    issue_id BIGSERIAL PRIMARY KEY,
    vendor_id INTEGER NOT NULL,
    pickup_datetime TIMESTAMP NOT NULL,
    pickup_date DATE NOT NULL,
    pickup_hour INTEGER NOT NULL,
    pickup_day_time TEXT NOT NULL,
    is_weekend BOOLEAN NOT NULL,
    time_period TEXT NOT NULL,
    pickup_borough TEXT NOT NULL,
    pickup_zone TEXT NOT NULL,

    dropoff_datetime TIMESTAMP NOT NULL,
    dropoff_borough TEXT NOT NULL,
    dropoff_zone TEXT NOT NULL,

    passenger_count INTEGER NOT NULL,

    trip_distance NUMERIC(10,2) NOT NULL,
    trip_duration_minutes NUMERIC(10,2) NOT NULL,

    rate_code_id INTEGER NOT NULL,
    store_and_fwd_flag TEXT NOT NULL,   
    pickup_location_id INTEGER NOT NULL,
    dropoff_location_id INTEGER NOT NULL,
    payment_type TEXT NOT NULL,
    fare_amount NUMERIC(10,2) NOT NULL,
    tip_amount NUMERIC(10,2) NOT NULL,
    total_amount NUMERIC(10,2) NOT NULL,
    error_type TEXT NOT NULL,

    CONSTRAINT fk_pickup
        FOREIGN KEY(pickup_location_id) 
        REFERENCES silver.taxi_zones(location_id),

    CONSTRAINT fk_dropoff
        FOREIGN KEY(dropoff_location_id) 
        REFERENCES silver.taxi_zones(location_id)
);