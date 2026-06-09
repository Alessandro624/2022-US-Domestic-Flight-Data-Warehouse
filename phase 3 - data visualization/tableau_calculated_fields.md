# Tableau Calculated Fields

This document lists the calculated fields used in the Tableau workbook
[`US_Departure_Disruptions_2022.twb`](US_Departure_Disruptions_2022.twb).
These fields belong to the visualization layer: they support dashboard filters,
bucketed comparisons, tooltips, and presentation-level indicators without
changing the dimensional warehouse generated in `data/4-data warehouse/`.

## Analytical Indicators

### IS DEPARTED FLIGHT

Identifies flights that actually departed. It is used to avoid artificial zero
values from cancelled flights when computing operational averages.

```tableau
[CANCELLATION_REASON] = "Not Cancelled"
```

### DEP DELAY RATE

Share of flights with a departure delay of at least 15 minutes.

```tableau
COUNTD(
    IF [DEP_DELAY] >= 15
    THEN [FLIGHT_ID]
    END
)
/
COUNTD([FLIGHT_ID])
```

### CANCELLATION RATE

Share of flights whose cancellation reason is different from `Not Cancelled`.

```tableau
COUNTD(
    IF NOT [IS DEPARTED FLIGHT]
    THEN [FLIGHT_ID]
    END
)
/
COUNTD([FLIGHT_ID])
```

### LOW VISIBILITY RATE

Share of flights observed with low but valid visibility.

```tableau
COUNTD(
    IF [VISIBILITY] > 0
       AND [VISIBILITY] <= 3
    THEN [FLIGHT_ID]
    END
)
/
COUNTD([FLIGHT_ID])
```

## Departed-Flight Averages

### AVG DEP DELAY DEPARTED

Average departure delay computed only for departed flights.

```tableau
AVG(
    IF [IS DEPARTED FLIGHT]
    THEN [DEP_DELAY]
    END
)
```

### AVG TAXI OUT DEPARTED

Average taxi-out time computed only for departed flights.

```tableau
AVG(
    IF [IS DEPARTED FLIGHT]
    THEN [TAXI_OUT]
    END
)
```

### AVG AIR TIME DEPARTED

Average air time computed only for departed flights.

```tableau
AVG(
    IF [IS DEPARTED FLIGHT]
    THEN [AIR_TIME]
    END
)
```

## Buckets

### VISIBILITY BUCKET

Groups visibility values in miles for weather-context comparisons.

```tableau
IF [VISIBILITY] = 0 THEN "0 mi"
ELSEIF [VISIBILITY] <= 2 THEN "0-2 mi"
ELSEIF [VISIBILITY] <= 4 THEN "2-4 mi"
ELSEIF [VISIBILITY] <= 6 THEN "4-6 mi"
ELSEIF [VISIBILITY] <= 8 THEN "6-8 mi"
ELSEIF [VISIBILITY] <= 10 THEN "8-10 mi"
ELSE ">10 mi"
END
```

### WIND GUST BUCKET

Groups wind gust values in knots.

```tableau
IF [WIND_GUST] <= 10 THEN "≤10 kt"
ELSEIF [WIND_GUST] <= 20 THEN "10-20 kt"
ELSEIF [WIND_GUST] <= 30 THEN "20-30 kt"
ELSE ">30 kt"
END
```

### TEMPERATURE BUCKET

Groups temperature values in Celsius.

```tableau
IF [TEMPERATURE] <= -10 THEN "≤ -10 °C"
ELSEIF [TEMPERATURE] <= 0 THEN "-10 to 0 °C"
ELSEIF [TEMPERATURE] <= 10 THEN "0 to 10 °C"
ELSEIF [TEMPERATURE] <= 20 THEN "10 to 20 °C"
ELSEIF [TEMPERATURE] <= 30 THEN "20 to 30 °C"
ELSE "> 30 °C"
END
```

### AIRCRAFT AGE BUCKET

Groups aircraft age into readable operational ranges.

```tableau
IF [AIRCRAFT_AGE] < 6 THEN "0-5 yr"
ELSEIF [AIRCRAFT_AGE] < 16 THEN "6-15 yr"
ELSEIF [AIRCRAFT_AGE] < 31 THEN "16-30 yr"
ELSE "31+ yr"
END
```
