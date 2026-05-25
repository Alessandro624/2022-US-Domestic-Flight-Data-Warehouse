# Data

This folder contains the project data layers. Each layer has a specific role in the data warehouse workflow, from the original source files to the final dimensional outputs.

## Structure

| Folder | Local guide | Role |
| --- | --- | --- |
| [1-original dataset](1-original%20dataset/) | [Original Dataset Placeholder.md](1-original%20dataset/Original%20Dataset%20Placeholder.md) | Original input files used as the starting point of the project. |
| [2-reconciled database](2-reconciled%20database/) | [Reconciled Database Placeholder.md](2-reconciled%20database/Reconciled%20Database%20Placeholder.md) | Intermediate reconciled layer aligned with the relational schema designed in Phase 1. |
| [3-cleaned database](3-cleaned%20database/) | [Cleaned Database Placeholder.md](3-cleaned%20database/Cleaned%20Database%20Placeholder.md) | Cleaned data produced after data quality assessment and transformation rules. |
| [4-data warehouse](4-data%20warehouse/) | [Data Warehouse Placeholder.md](4-data%20warehouse/Data%20Warehouse%20Placeholder.md) | Final dimensional output, including dimensions and fact tables used for analysis. |

## Data Flow

```mermaid
flowchart LR
    A["1-original dataset"] --> B["2-reconciled database"]
    B --> C["3-cleaned database"]
    C --> D["4-data warehouse"]
```

## Usage

The data folders are populated and updated by the notebooks in [phase 2 - etl](../phase%202%20-%20etl/README.md). The recommended execution order is described there.
