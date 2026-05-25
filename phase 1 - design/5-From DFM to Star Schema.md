# From DFM to Star Schema

## Dimensional Fact Model (DFM)

![Dimensional Fact Model](images/DFM%20Schema.jpg)

## Glossary of Measures

The following table details the measures extracted from the Dimensional Fact Model, along with the aggregation formulas used in the measure glossary.

| Measure Name | Formula / Expression |
| :--- | :--- |
| # OF FLIGHTS | COUNT(*) |
| AVG_DELAY | AVG(DEP_DELAY) |
| SUM_DELAY | SUM(DEP_DELAY) |
| MAX_DELAY | MAX(DEP_DELAY) |
| DELAY_RATE | SUM(CASE WHEN DEP_DELAY > 15 THEN 1 ELSE 0 END) / COUNT(*) |
| CANCELLATION_RATE | CANCELLED_FLIGHTS / COUNT(*) |
| AVG_TAXI_OUT | AVG(TAXI_OUT) |
| AVG_AIR_TIME | AVG(AIR_TIME) |
| AVG_DISTANCE | AVG(DISTANCE) |
| AVG_WIND_SPD | AVG(WIND_SPD) |
| MAX_WIND_GUST | MAX(WIND_GUST) |
| AVG_VISIBILITY | AVG(VISIBILITY) |
| LOW_VISIBILITY_RATE | SUM(CASE WHEN VISIBILITY > 0 AND VISIBILITY <= 3 THEN 1 ELSE 0 END) / COUNT(*) |
| AVG_TEMPERATURE | AVG(TEMPERATURE) |
| MIN_TEMPERATURE | MIN(TEMPERATURE) |
| AVG_CLOUD_COVER | AVG(CLOUD_COVER) |

## Star Schema

![Star Schema](images/Star%20schema.png)
