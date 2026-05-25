# Phase 2 - ETL

This phase contains the executable workflow used to analyze, clean, transform, and load the data warehouse tables.

## Recommended Execution Order

| Step | Notebook | Purpose |
| --- | --- | --- |
| 0 | [0-Preliminary Analysis.ipynb](0-Preliminary%20Analysis.ipynb) | Inspect the source dataset and describe the original attributes. |
| 1 | [1-Data Quality Assessment.ipynb](1-Data%20Quality%20Assessment.ipynb) | Evaluate schema issues, duplicates, missing values, and data quality indicators. |
| 2 | [2-LLM Data Quality Assessment.ipynb](2-LLM%20Data%20Quality%20Assessment.ipynb) | Supporting review for the data quality assessment. |
| 3 | [3-Missing Values and Outliers.ipynb](3-Missing%20Values%20and%20Outliers.ipynb) | Analyze missingness patterns and relevant outlier cases. |
| 4 | [4-LLM Missing Values and Outliers.ipynb](4-LLM%20Missing%20Values%20and%20Outliers.ipynb) | Supporting review for missingness and outlier decisions. |
| 5 | [5-Cleaning Pipeline.ipynb](5-Cleaning%20Pipeline.ipynb) | Apply the cleaning rules and produce the cleaned layer. |
| 6 | [6-LLM Cleaning Pipeline.ipynb](6-LLM%20Cleaning%20Pipeline.ipynb) | Supporting review for the cleaning pipeline. |
| 7 | [7-From DFM to Star Schema.ipynb](7-From%20DFM%20to%20Star%20Schema.ipynb) | Validate the dimensional design and prepare star schema mappings. |
| 8 | [8-LLM From DFM to Star Schema.ipynb](8-LLM%20From%20DFM%20to%20Star%20Schema.ipynb) | Supporting review for the dimensional transformation. |
| 9 | [9-ETL Pipeline.ipynb](9-ETL%20Pipeline.ipynb) | Build and export dimensions and fact tables. |
| 10 | [10-LLM ETL Pipeline.ipynb](10-LLM%20ETL%20Pipeline.ipynb) | Supporting review for the final ETL pipeline. |

## Utilities

The [utils](utils/) folder contains shared functions used by the notebooks.

## Outputs

The notebooks write their main results into the corresponding folders under [data](../data/README.md), ending with the dimensional tables in `data/4-data warehouse`.
