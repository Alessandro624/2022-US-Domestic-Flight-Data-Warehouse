# Data Profiling and Preliminary Analysis Report

## 1. Data Dictionary

### COMPLETEDATA.CSV

| Column | Type | Description |
| :--- | :--- | :--- |
| FL_DATE | object | Date of flight |
| DEP_HOUR | int64 | Departure hour (0-23) |
| MKT_UNIQUE_CARRIER | object | Marketing Carrier Unique Code -> Carrier.Code |
| MKT_CARRIER_FL_NUM | int64 | Marketing Carrier Flight Number |
| OP_UNIQUE_CARRIER | object | Operating Carrier Unique Code -> Carrier.Code |
| OP_CARRIER_FL_NUM | int64 | Operating Carrier Flight Number |
| TAIL_NUM | object | FAA N-Number/Registration -> Aircraft.Tail_Num |
| ORIGIN | object | Origin airport code -> Station.Airport |
| DEST | object | Destination airport code -> Station.Airport |
| DEP_TIME | object | Actual departure timestamp |
| CRS_DEP_TIME | object | Scheduled departure timestamp (CRS) |
| TAXI_OUT | int64 | Taxi-out time (in minutes) |
| DEP_DELAY | int64 | Departure delay (in minutes; negative = early) |
| AIR_TIME | int64 | Wheels-off to wheels-on time (in minutes) |
| DISTANCE | int64 | Flight distance (in miles) |
| CANCELLED | int64 | Cancellation status -> Cancellation.Status |
| LATITUDE | float64 | Latitude coordinate |
| LONGITUDE | float64 | Longitude coordinate |
| ELEVATION | int64 | Elevation (in ft) |
| MESONET_STATION | object | Mesonet station code (UNIQUE) |
| YEAR_OF_MANUFACTURE | int64 | Year aircraft was manufactured |
| MANUFACTURER | object | Aircraft manufacturer name |
| ICAO_TYPE | object | ICAO aircraft type designator |
| RANGE | object | Encoded range category (Short/Medium/Long Range) |
| WIDTH | object | Aircraft body type (Narrow Body or Wide Body) |
| WIND_DIR | float64 | Wind direction (degrees) |
| WIND_SPD | float64 | Wind speed (in kt) |
| WIND_GUST | float64 | Wind gust speed (in kt) |
| VISIBILITY | float64 | Visibility (in miles) |
| TEMPERATURE | float64 | Temperature (in Celsius) |
| DEW_POINT | float64 | Dew point (in Celsius) |
| REL_HUMIDITY | float64 | Relative humidity (percentage) |
| ALTIMETER | float64 | Altimeter setting (in Hg) |
| LOWEST_CLOUD_LAYER | float64 | Height of lowest cloud layer (in ft) |
| N_CLOUD_LAYER | float64 | Number of cloud layers |
| LOW_LEVEL_CLOUD | float64 | Low-level cloud present (height below 6500 ft) |
| MID_LEVEL_CLOUD | float64 | Mid-level cloud present (between 6500 and 20000 ft) |
| HIGH_LEVEL_CLOUD | float64 | High-level cloud present (height above 20000 ft) |
| CLOUD_COVER | float64 | Cloud cover value |
| ACTIVE_WEATHER | float64 | Active weather condition -> Active_Weather.Status |

### ACTIVEWEATHER.CSV

| Column | Type | Description |
| :--- | :--- | :--- |
| STATUS | int64 | Primary Key of the status |
| WEATHER_DESCRIPTION | object | Description of active weather condition |

### CANCELLATION.CSV

| Column | Type | Description |
| :--- | :--- | :--- |
| STATUS | int64 | Primary Key of the status |
| CANCELLATION_REASON | object | Reason for cancellation |

### CARRIERS.CSV

| Column | Type | Description |
| :--- | :--- | :--- |
| CODE | object | PK - Carrier unique code |
| DESCRIPTION | object | Full carrier name or status description |

### STATIONS.CSV

| Column | Type | Description |
| :--- | :--- | :--- |
| AIRPORT_ID | int64 | Internal numeric airport ID |
| AIRPORT | object | PK - Airport code (e.g., JFK) |
| DISPLAY_AIRPORT_NAME | object | Full airport name |
| DISPLAY_AIRPORT_CITY_NAME_FULL | object | Full city name |
| AIRPORT_STATE_NAME | object | Full state name |
| AIRPORT_STATE_CODE | object | State abbreviation |
| LATITUDE | float64 | Latitude coordinate |
| LONGITUDE | float64 | Longitude coordinate |
| ELEVATION | int64 | Elevation (in ft) |
| ICAO | object | ICAO airport code (UNIQUE) |
| IATA | object | IATA airport code (UNIQUE) |
| FAA | object | FAA identifier |
| MESONET_STATION | object | Mesonet station code (UNIQUE) |

## 2. Main Dataset Overview

- Analyzed file: CompleteData.csv
- Total rows: 6,954,636
- Total columns: 40

## 3. Functional Dependencies Analysis

### (MESONET_STATION, FL_DATE, DEP_HOUR) -> Weather Attributes

- Total groups analyzed: 1,133,884
- Violations found: 0
- Result: SUCCESS. The functional dependency is valid across the dataset.

### Geographic Mapping: Airports and Weather Stations

- ORIGIN to MESONET_STATION: Origin airports mapped to multiple stations: 0 out of 375
- MESONET_STATION to ORIGIN: Stations mapped to multiple origin airports: 0 out of 375

Exclusion Test (DEST vs MESONET_STATION)

- DEST to MESONET_STATION: Destinations mapped to multiple stations: 311 out of 376.
Note: The very high percentage of violations on DEST, opposed to the uniqueness on ORIGIN, provides empirical certainty that the MESONET_STATION attribute recorded in the flight record refers exclusively to the weather conditions of the departure airport.

## 4. Consistency Analysis (Cancelled Flights)

- Total cancelled flights analyzed: 147,830

### Departure Metrics (DEP_TIME and DEP_DELAY)

- DEP_TIME NULL: 0 (0.00%)
- DEP_TIME aligned to FL_DATE and DEP_HOUR: 147,830 / 147,830 (100.00%)
- DEP_DELAY NULL: 0 (0.00%)
- DEP_DELAY equals 0: 143,770 (97.25%)

### Operational Anomalies Checks

- Cancelled flights with AIR_TIME > 0 or TAXI_OUT > 0: 810
- Cancelled flights with only AIR_TIME > 0 recorded: 0
