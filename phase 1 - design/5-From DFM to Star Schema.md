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
| AVG_TAXI_OUT | AVG(TAXI_OUT) |
| AVG_AIR_TIME | AVG(AIR_TIME) |
| AVG_DISTANCE | AVG(DISTANCE) |
| AVG_WIND_SPD | AVG(WIND_SPD) |
| MAX_WIND_GUST | MAX(WIND_GUST) |
| MIN_VISIBILITY | MIN(VISIBILITY) |
| AVG_TEMPERATURE | AVG(TEMPERATURE) |
| MIN_TEMPERATURE | MIN(TEMPERATURE) |
| AVG_CLOUD_COVER | AVG(CLOUD_COVER) |

## Star Schema

![Star Schema](images/Star%20schema.png)
