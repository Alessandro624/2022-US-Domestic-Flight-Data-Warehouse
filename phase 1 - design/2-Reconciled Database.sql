-- ============================================================
--  RECONCILED DATABASE
--  PostgreSQL DDL
-- ============================================================

-- ------------------------------------------------------------
--  1. AIRCRAFTS
-- ------------------------------------------------------------
CREATE TABLE IF NOT EXISTS AIRCRAFTS (
    TAIL_NUM             VARCHAR(20)  PRIMARY KEY,
    YEAR_OF_MANUFACTURE  INTEGER,
    MANUFACTURER         VARCHAR(100),
    ICAO_TYPE            VARCHAR(20),
    RANGE                VARCHAR(50),
    WIDTH                VARCHAR(50)
);

-- ------------------------------------------------------------
--  2. CARRIERS
-- ------------------------------------------------------------
CREATE TABLE IF NOT EXISTS CARRIERS (
    CODE        VARCHAR(10)  PRIMARY KEY,
    DESCRIPTION VARCHAR(150)
);

-- ------------------------------------------------------------
--  3. ACTIVE_WEATHER
-- ------------------------------------------------------------
CREATE TABLE IF NOT EXISTS ACTIVE_WEATHER (
    STATUS              INTEGER      PRIMARY KEY,
    WEATHER_DESCRIPTION VARCHAR(200)
);

-- ------------------------------------------------------------
--  4. CANCELLATION
-- ------------------------------------------------------------
CREATE TABLE IF NOT EXISTS CANCELLATION (
    STATUS              INTEGER      PRIMARY KEY,
    CANCELLATION_REASON VARCHAR(100)
);

-- ------------------------------------------------------------
--  5. STATIONS
-- ------------------------------------------------------------
CREATE TABLE IF NOT EXISTS STATIONS (
    AIRPORT                        VARCHAR(10)   PRIMARY KEY,
    AIRPORT_ID                     INTEGER,
    DISPLAY_AIRPORT_NAME           VARCHAR(150),
    DISPLAY_AIRPORT_CITY_NAME_FULL VARCHAR(150),
    AIRPORT_STATE_NAME             VARCHAR(100),
    AIRPORT_STATE_CODE             VARCHAR(10),
    LATITUDE                       DOUBLE PRECISION,
    LONGITUDE                      DOUBLE PRECISION,
    ELEVATION                      INTEGER,
    ICAO                           VARCHAR(10),
    IATA                           VARCHAR(10),
    FAA                            VARCHAR(10),
    MESONET_STATION                VARCHAR(10)
);

-- ------------------------------------------------------------
--  6. WEATHER_OBSERVATIONS
-- ------------------------------------------------------------
CREATE TABLE IF NOT EXISTS WEATHER_OBSERVATIONS (
    OBS_ID                SERIAL          PRIMARY KEY,
    ORIGIN_AIRPORT        VARCHAR(10),
    OBS_DATE              DATE,
    OBS_HOUR              SMALLINT,
    WIND_DIR              DOUBLE PRECISION,
    WIND_SPD              DOUBLE PRECISION,
    WIND_GUST             DOUBLE PRECISION,
    VISIBILITY            DOUBLE PRECISION,
    TEMPERATURE           DOUBLE PRECISION,
    DEW_POINT             DOUBLE PRECISION,
    REL_HUMIDITY          DOUBLE PRECISION,
    ALTIMETER             DOUBLE PRECISION,
    LOWEST_CLOUD_LAYER    DOUBLE PRECISION,
    N_CLOUD_LAYER         NUMERIC(6,2),
    LOW_LEVEL_CLOUD       NUMERIC(3,1),
    MID_LEVEL_CLOUD       NUMERIC(3,1),
    HIGH_LEVEL_CLOUD      NUMERIC(3,1),
    CLOUD_COVER           NUMERIC(3,1),
    ACTIVE_WEATHER_STATUS NUMERIC(3,1)
);

-- ------------------------------------------------------------
--  7. FLIGHTS
-- ------------------------------------------------------------
CREATE TABLE IF NOT EXISTS FLIGHTS (
    FLIGHT_ID              SERIAL          PRIMARY KEY,

    -- temporal
    FL_DATE                DATE,
    DEP_HOUR               SMALLINT,

    -- carriers
    MKT_UNIQUE_CARRIER     VARCHAR(10),
    MKT_CARRIER_FL_NUM     INTEGER,
    OP_UNIQUE_CARRIER      VARCHAR(10),
    OP_CARRIER_FL_NUM      INTEGER,

    -- aircraft
    TAIL_NUM               VARCHAR(20),

    -- airports
    ORIGIN                 VARCHAR(10),
    DEST                   VARCHAR(10),

    -- schedule & performance
    DEP_TIME               TIMESTAMP,
    CRS_DEP_TIME           TIMESTAMP,
    TAXI_OUT               INTEGER,
    DEP_DELAY              INTEGER,
    AIR_TIME               INTEGER,
    DISTANCE               DOUBLE PRECISION,

    -- cancellation
    CANCELLED              INTEGER,

    -- weather
    WEATHER_OBSERVATION_ID INTEGER
);

-- ------------------------------------------------------------
--  INDEXES FOR PERFORMANCE
-- ------------------------------------------------------------
CREATE INDEX IF NOT EXISTS IDX_FLIGHTS_FL_DATE      ON FLIGHTS(FL_DATE);
CREATE INDEX IF NOT EXISTS IDX_FLIGHTS_ORIGIN       ON FLIGHTS(ORIGIN);
CREATE INDEX IF NOT EXISTS IDX_FLIGHTS_DEST         ON FLIGHTS(DEST);
CREATE INDEX IF NOT EXISTS IDX_FLIGHTS_MKT_CARRIER  ON FLIGHTS(MKT_UNIQUE_CARRIER);
CREATE INDEX IF NOT EXISTS IDX_FLIGHTS_OP_CARRIER   ON FLIGHTS(OP_UNIQUE_CARRIER);
CREATE INDEX IF NOT EXISTS IDX_FLIGHTS_CANCELLED    ON FLIGHTS(CANCELLED);
CREATE INDEX IF NOT EXISTS IDX_WEATHER_NATURAL_KEY  ON WEATHER_OBSERVATIONS(ORIGIN_AIRPORT, OBS_DATE, OBS_HOUR);

-- ------------------------------------------------------------
-- WEATHER_OBSERVATIONS -> FLIGHTS AFTER DATA LOAD
-- ------------------------------------------------------------
-- UPDATE FLIGHTS f
-- SET WEATHER_OBSERVATION_ID = w.OBS_ID
-- FROM WEATHER_OBSERVATIONS w
-- WHERE f.ORIGIN = w.ORIGIN_AIRPORT
--   AND f.FL_DATE = w.OBS_DATE
--   AND f.DEP_HOUR = w.OBS_HOUR
--   AND f.WEATHER_OBSERVATION_ID IS NULL;