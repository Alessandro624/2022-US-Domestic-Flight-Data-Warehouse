-- ============================================================
--  DATA WAREHOUSE - (FROM STAR SCHEMA)
--  PostgreSQL DDL
-- ============================================================

-- ------------------------------------------------------------
--  1. DIMENSION: DIM_FL_DATES
-- ------------------------------------------------------------
CREATE TABLE IF NOT EXISTS DIM_FL_DATES (
    FL_DATE_ID  SERIAL      PRIMARY KEY,
    FL_DATE     DATE        NOT NULL,
    DAY_OF_WEEK VARCHAR(10),            -- e.g. 'Monday', 'Tuesday'
    IS_HOLIDAY  BOOLEAN,
    MONTH       SMALLINT,
    QUARTER     SMALLINT,
    YEAR        SMALLINT,
    LOAD_TIMESTAMP TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- ------------------------------------------------------------
--  2. DIMENSION: DIM_DEP_HOURS
-- ------------------------------------------------------------
CREATE TABLE IF NOT EXISTS DIM_DEP_HOURS (
    DEP_HOUR_ID SERIAL      PRIMARY KEY,
    DEP_HOUR    SMALLINT,               -- 0 to 23
    TIME_BAND   VARCHAR(20),            -- Night(0-3), Early Morning(4-7), Morning(8-11), Afternoon(12-15), Evening(16-19), Late Evening(20-23)
    LOAD_TIMESTAMP TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- ------------------------------------------------------------
--  3. DIMENSION: DIM_STATIONS
-- ------------------------------------------------------------
CREATE TABLE IF NOT EXISTS DIM_STATIONS (
    STATION_ID   SERIAL      PRIMARY KEY,
    AIRPORT_CODE CHAR(4)     NOT NULL,
    AIRPORT_NAME VARCHAR(150),
    CITY         VARCHAR(100),
    STATE        VARCHAR(50),
    LATITUDE     NUMERIC(9,6),
    LONGITUDE    NUMERIC(9,6),
    LOAD_TIMESTAMP TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- ------------------------------------------------------------
--  4. DIMENSION: DIM_CARRIERS
-- ------------------------------------------------------------
CREATE TABLE IF NOT EXISTS DIM_CARRIERS (
    CARRIER_ID  SERIAL      PRIMARY KEY,
    DESCRIPTION VARCHAR(100) NOT NULL,
    LOAD_TIMESTAMP TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- ------------------------------------------------------------
--  5. DIMENSION: DIM_JUNK
--  (Contains low-cardinality descriptors)
-- ------------------------------------------------------------
CREATE TABLE IF NOT EXISTS DIM_JUNK (
    JUNK_ID             SERIAL       PRIMARY KEY,
    CANCELLATION_REASON VARCHAR(60),
    WEATHER_DESCRIPTION VARCHAR(150),
    LOAD_TIMESTAMP TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- ------------------------------------------------------------
--  6. DIMENSION: DIM_AIRCRAFTS
-- ------------------------------------------------------------
CREATE TABLE IF NOT EXISTS DIM_AIRCRAFTS (
    AIRCRAFT_ID    SERIAL       PRIMARY KEY,
    TAIL_NUM       CHAR(10)     NOT NULL,
    MANUFACTURER   VARCHAR(50),
    AIRCRAFT_AGE   SMALLINT,
    LOAD_TIMESTAMP TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- ------------------------------------------------------------
--  7. FACT TABLE: FLIGHTS
-- ------------------------------------------------------------
CREATE TABLE IF NOT EXISTS FLIGHTS (
    FLIGHT_ID    SERIAL       PRIMARY KEY,
    FL_DATE_ID        INTEGER      NOT NULL REFERENCES DIM_FL_DATES(FL_DATE_ID),
    DEP_HOUR_ID       INTEGER      NOT NULL REFERENCES DIM_DEP_HOURS(DEP_HOUR_ID),
    ORIGIN_STATION_ID INTEGER      NOT NULL REFERENCES DIM_STATIONS(STATION_ID),
    DEST_STATION_ID   INTEGER      NOT NULL REFERENCES DIM_STATIONS(STATION_ID),
    MKT_CARRIER_ID    INTEGER      NOT NULL REFERENCES DIM_CARRIERS(CARRIER_ID),
    OP_CARRIER_ID     INTEGER      NOT NULL REFERENCES DIM_CARRIERS(CARRIER_ID),
    AIRCRAFT_ID       INTEGER      NOT NULL REFERENCES DIM_AIRCRAFTS(AIRCRAFT_ID),
    JUNK_ID           INTEGER      NOT NULL REFERENCES DIM_JUNK(JUNK_ID),
    -- Measures (Environmental)
    WIND_SPD          NUMERIC(5,1),
    WIND_GUST         NUMERIC(5,1),
    VISIBILITY        NUMERIC(5,1),
    TEMPERATURE       NUMERIC(5,2),
    CLOUD_COVER       NUMERIC(5,1),
    -- Measures (Performance)
    DEP_DELAY         NUMERIC(6,1),
    TAXI_OUT          NUMERIC(6,1),
    AIR_TIME          NUMERIC(6,1),
    DISTANCE          NUMERIC(7,1),
    LOAD_TIMESTAMP    TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- ------------------------------------------------------------
--  INDEXES
-- ------------------------------------------------------------
CREATE INDEX IF NOT EXISTS IDX_FLIGHTS_DATE     ON FLIGHTS(FL_DATE_ID);
CREATE INDEX IF NOT EXISTS IDX_FLIGHTS_HOUR     ON FLIGHTS(DEP_HOUR_ID);
CREATE INDEX IF NOT EXISTS IDX_FLIGHTS_ORIGIN   ON FLIGHTS(ORIGIN_STATION_ID);
CREATE INDEX IF NOT EXISTS IDX_FLIGHTS_DEST     ON FLIGHTS(DEST_STATION_ID);
CREATE INDEX IF NOT EXISTS IDX_FLIGHTS_MKT      ON FLIGHTS(MKT_CARRIER_ID);
CREATE INDEX IF NOT EXISTS IDX_FLIGHTS_OP       ON FLIGHTS(OP_CARRIER_ID);
CREATE INDEX IF NOT EXISTS IDX_FLIGHTS_AIRCRAFT ON FLIGHTS(AIRCRAFT_ID);
CREATE INDEX IF NOT EXISTS IDX_FLIGHTS_JUNK     ON FLIGHTS(JUNK_ID);
