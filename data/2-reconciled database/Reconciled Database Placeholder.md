# Reconciled Database

## Overview

This directory contains the **reconciled database** derived from the original Kaggle dataset. The reconciliation process involves:

1. Creating a PostgreSQL database schema
2. Loading original CSV data
3. Applying reconciliation transformations
4. Exporting tables

**Expected structure after completion:**

```text
data/
└── 2-reconciled database/
    ├── Active_Weather.csv
    ├── Aircrafts.csv
    ├── Cancellation.csv
    ├── Carriers.csv
    ├── Flights.csv
    ├── Stations.csv
    └── Weather_Observations.csv
```

---

## Prerequisites

### Data Requirements

- Original dataset files in `data/1-original dataset/`
  - ActiveWeather.csv
  - Cancellation.csv
  - Carriers.csv
  - CompleteData.csv
  - Stations.csv

---

## Execute Reconciliation Transformations

**Run the UPDATE query at the end of the reconciled database [SQL file](../../phase%201%20-%20design/2-Reconciled%20Database.sql):**

```sql
-- Link FLIGHTS to WEATHER_OBSERVATIONS based on temporal/spatial matching
UPDATE FLIGHTS f
SET WEATHER_OBSERVATION_ID = w.OBS_ID
FROM WEATHER_OBSERVATIONS w
WHERE f.ORIGIN = w.ORIGIN_AIRPORT
  AND f.FL_DATE = w.OBS_DATE
  AND f.DEP_HOUR = w.OBS_HOUR
  AND f.WEATHER_OBSERVATION_ID IS NULL;
```

---
