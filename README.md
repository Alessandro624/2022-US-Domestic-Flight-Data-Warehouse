# US Domestic Flight Data Warehouse

A data warehouse project focused on 2022 US domestic airline departures. The project starts from raw flight and weather data, evaluates data quality issues, applies cleaning and transformation rules, and produces a dimensional model ready for analytical reporting.

The work follows an academic data warehouse development workflow: source analysis, conceptual and logical design, data quality assessment, ETL design, star schema implementation, and final reporting.

## Project Objectives

- Analyze the original operational data and identify the relevant entities, attributes, measures, and analytical requirements.
- Design a reconciled relational database that provides a consistent intermediate layer before dimensional modeling.
- Assess data quality, including missing values, duplicates, inconsistent values, outliers, and schema-level issues.
- Apply a reproducible cleaning pipeline while preserving the rationale behind each transformation.
- Define the Dimensional Fact Model and translate it into a star schema aligned with the project requirements.
- Implement an ETL pipeline that produces dimensions and fact tables suitable for OLAP-style analysis.
- Document the design choices, data quality decisions, ETL process, and final warehouse structure in a concise academic report.

## Repository Map

| Area | Description |
| --- | --- |
| [data](data/README.md) | Data layers used throughout the project, from the original dataset to the final warehouse outputs. |
| [phase 1 - design](phase%201%20-%20design/README.md) | Source of truth for the project design: reconciled schema, attribute tree, DFM, and star schema. |
| [phase 2 - etl](phase%202%20-%20etl/README.md) | Jupyter notebooks and utilities for profiling, cleaning, dimensional transformation, and ETL. |
| [phase 4 - report](phase%204%20-%20report/README.md) | Final report sources, generated figures, references, and compiled PDF. |

## Development Flow

```mermaid
flowchart LR
    A["Original CSV files"] --> B["Reconciled database"]
    B --> C["Data quality assessment"]
    C --> D["Cleaning pipeline"]
    D --> E["Dimensional modeling"]
    E --> F["Star schema"]
    F --> G["ETL output"]
    G --> H["Final report"]
```

## How to Navigate the Project

1. Start from [phase 1 - design](phase%201%20-%20design/README.md) to understand the modeling choices.
2. Review [data](data/README.md) to understand the role of each data layer.
3. Execute the notebooks in [phase 2 - etl](phase%202%20-%20etl/README.md) in numerical order.
4. Use [phase 4 - report](phase%204%20-%20report/README.md) to inspect the final academic deliverable and its generated figures.

## Main Outputs

- Reconciled database design and SQL schema.
- Data quality assessment and cleaning workflow.
- Dimensional Fact Model and star schema.
- ETL pipeline producing dimension and fact tables.
- Final academic report with figures, tables, and bibliography.
