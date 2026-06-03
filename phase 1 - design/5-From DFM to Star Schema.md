# From DFM to Star Schema

## Dimensional Fact Model (DFM)

![Dimensional Fact Model](images/DFM%20Schema.jpg)

## Glossary of Measures

The following table defines the analytical aggregations and rates used in the report and Tableau dashboards.

| Measure Name | Formula / Expression |
| :--- | :--- |
| # OF FLIGHTS | COUNT(*) |
| AVG_DELAY | AVG(DEP_DELAY) |
| DELAY_RATE | SUM(CASE WHEN DEP_DELAY > 15 THEN 1 ELSE 0 END) / COUNT(*) |
| CANCELLATION_RATE | SUM(CASE WHEN CANCELLATION_REASON <> "Not Cancelled" THEN 1 ELSE 0 END) / COUNT(*) |
| AVG_TAXI_OUT | AVG(TAXI_OUT) |
| AVG_AIR_TIME | AVG(AIR_TIME) |
| AVG_DISTANCE | AVG(DISTANCE) |
| AVG_WIND_SPD | AVG(WIND_SPD) |
| AVG_VISIBILITY | AVG(VISIBILITY) |
| LOW_VISIBILITY_RATE | SUM(CASE WHEN VISIBILITY > 0 AND VISIBILITY <= 3 THEN 1 ELSE 0 END) / COUNT(*) |
| MIN_TEMPERATURE | MIN(TEMPERATURE) |
| AVG_CLOUD_COVER | AVG(CLOUD_COVER) |

## Star Schema

![Star Schema](images/Star%20schema.png)
