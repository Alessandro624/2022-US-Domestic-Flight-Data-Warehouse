# Phase 1 - Design

This phase is the source of truth for the project design. It documents the main modeling choices before the ETL notebooks are executed.

## Contents

| File | Purpose |
| --- | --- |
| [0-Preliminary Analysis.md](0-Preliminary%20Analysis.md) | Initial analysis of the source dataset, relevant attributes, and expected analytical needs. |
| [1-Schema of the Reconciled Database.md](1-Schema%20of%20the%20Reconciled%20Database.md) | Description of the reconciled relational schema. |
| [2-Reconciled Database.sql](2-Reconciled%20Database.sql) | SQL definition of the reconciled database. |
| [3-Attribute Tree.md](3-Attribute%20Tree.md) | Initial attribute tree used to reason about dimensions and hierarchies. |
| [4-Updated Attribute Tree.md](4-Updated%20Attribute%20Tree.md) | Updated attribute tree after refinement. |
| [5-From DFM to Star Schema.md](5-From%20DFM%20to%20Star%20Schema.md) | Translation from the Dimensional Fact Model to the final star schema. |
| [6-Data Warehouse.sql](6-Data%20Warehouse.sql) | SQL definition of the final data warehouse schema. |
| [images](images/) | Design diagrams and schema images used by the project documentation. |

## Design Role

The decisions in this folder guide the implementation in the ETL notebooks. In particular, dimension names, fact table structure, hierarchies, and measures should remain aligned with this phase.
