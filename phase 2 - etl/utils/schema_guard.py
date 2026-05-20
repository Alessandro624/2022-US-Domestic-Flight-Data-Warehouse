import pandas as pd
from dataclasses import dataclass, field
from typing import Optional


@dataclass
class ColumnSchema:
    name: str
    dtype: str
    nullable: bool = True


@dataclass
class TableSchema:
    table_name: str
    columns: list[ColumnSchema] = field(default_factory=list)
    n_rows: Optional[int] = None
    pk: Optional[str] = None

    @property
    def col_names(self) -> set[str]:
        return {c.name for c in self.columns}

    @property
    def n_cols(self) -> int:
        return len(self.columns)


class SchemaContract:
    """
    Register expected schemas and validate DataFrames against them.

    Design principles:
    - Register once (after first clean load)
    - Validate after every load or transformation
    - Fail loudly on structural changes (column added/removed/renamed)
    - Warn softly on dtype changes (may be benign)
    """

    def __init__(self):
        self._schemas: dict[str, TableSchema] = {}

    def register(self, table_name: str, df: pd.DataFrame, pk: str = None):
        """Capture the expected schema from a reference DataFrame."""
        columns = [
            ColumnSchema(
                name=col,
                dtype=str(df[col].dtype),
                nullable=df[col].isna().any(),
            )
            for col in df.columns
        ]
        self._schemas[table_name] = TableSchema(
            table_name=table_name,
            columns=columns,
            n_rows=len(df),
            pk=pk,
        )
        return self

    def validate(self, table_name: str, df: pd.DataFrame, strict: bool = True) -> dict:
        """
        Validate a DataFrame against the registered schema.
        """
        if table_name not in self._schemas:
            return {
                "table": table_name,
                "status": "SKIP",
                "details": [{"check": "registration", "status": "SKIP", "message": f"Table '{table_name}' not registered"}],
            }

        schema = self._schemas[table_name]
        actual_cols = set(df.columns)
        expected_cols = schema.col_names
        details = []

        # 1. Column count
        n_expected = schema.n_cols
        n_actual = len(df.columns)
        if n_expected == n_actual:
            details.append({"check": "column_count", "status": "PASS", "message": f"{n_actual} columns (expected {n_expected})"})
        else:
            details.append({"check": "column_count", "status": "FAIL", "message": f"Expected {n_expected} columns, got {n_actual}"})

        # 2. Missing columns
        missing = expected_cols - actual_cols
        if missing:
            details.append({"check": "missing_columns", "status": "FAIL", "message": f"Missing columns: {sorted(missing)}"})
        else:
            details.append({"check": "missing_columns", "status": "PASS", "message": "All expected columns present"})

        # 3. Extra columns
        extra = actual_cols - expected_cols
        if extra:
            status = "FAIL" if strict else "WARN"
            details.append({"check": "extra_columns", "status": status, "message": f"Extra columns: {sorted(extra)}"})
        else:
            details.append({"check": "extra_columns", "status": "PASS", "message": "No unexpected columns"})

        # 4. Column order (soft check)
        expected_order = [c.name for c in schema.columns]
        actual_order = list(df.columns)
        common = [c for c in expected_order if c in actual_order]
        actual_common = [c for c in actual_order if c in expected_cols]
        if common == actual_common:
            details.append({"check": "column_order", "status": "PASS", "message": "Column order preserved"})
        else:
            details.append({"check": "column_order", "status": "WARN", "message": "Column order differs from registration"})

        # 5. Dtype changes
        dtype_changes = []
        for col_schema in schema.columns:
            if col_schema.name in actual_cols:
                actual_dtype = str(df[col_schema.name].dtype)
                if actual_dtype != col_schema.dtype:
                    dtype_changes.append(f"{col_schema.name}: expected {col_schema.dtype}, got {actual_dtype}")
        if dtype_changes:
            details.append({"check": "dtype_changes", "status": "WARN", "message": f"Dtype changes: {dtype_changes}"})
        else:
            details.append({"check": "dtype_changes", "status": "PASS", "message": "All dtypes match"})

        # 6. PK uniqueness (if pk registered)
        if schema.pk and schema.pk in actual_cols:
            dup = df[schema.pk].duplicated().sum()
            if dup == 0:
                details.append({"check": "pk_uniqueness", "status": "PASS", "message": f"PK '{schema.pk}' is unique"})
            else:
                details.append({"check": "pk_uniqueness", "status": "FAIL", "message": f"PK '{schema.pk}' has {dup} duplicates"})

        # Overall status
        statuses = [d["status"] for d in details]
        if "FAIL" in statuses:
            overall = "FAIL"
        elif "WARN" in statuses:
            overall = "WARN"
        else:
            overall = "PASS"

        return {"table": table_name, "status": overall, "details": details}

    def validate_all(self, dfs: dict[str, pd.DataFrame], strict: bool = True) -> dict:
        """Validate all registered tables against the provided dict of DataFrames."""
        results = {}
        all_details = []
        failures = 0

        for table_name in self._schemas:
            if table_name in dfs:
                result = self.validate(table_name, dfs[table_name], strict=strict)
                results[table_name] = result
                all_details.extend(result["details"])
                if result["status"] == "FAIL":
                    failures += 1

        return {"results": results, "details": all_details, "failures": failures}

    def assert_valid(self, table_name: str, df: pd.DataFrame, strict: bool = True):
        """Like validate(), but raises AssertionError on FAIL."""
        result = self.validate(table_name, df, strict=strict)
        failures = [d for d in result["details"] if d["status"] == "FAIL"]
        if failures:
            msgs = "; ".join(f"{d['check']}: {d['message']}" for d in failures)
            raise AssertionError(f"Schema validation FAILED for '{table_name}': {msgs}")

    @property
    def registered_tables(self) -> list[str]:
        return list(self._schemas.keys())
