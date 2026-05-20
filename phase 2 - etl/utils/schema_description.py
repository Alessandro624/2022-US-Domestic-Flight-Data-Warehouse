import pandas as pd


def _sample_value(series: pd.Series, max_rows_sample: int) -> str:
    values = series.dropna().head(max_rows_sample)
    if values.empty:
        return "--"
    return str(values.iloc[0])[:30]


def build_schema_description(dfs: dict, schema: dict, max_rows_sample: int = 5) -> str:
    """Build a compact textual description of the reconciled DB schema."""
    parts = ["SOURCE TABLES (cleaned):"]
    for name, df in dfs.items():
        parts.append(f"  TABLE {name}:")
        parts.append(f"    rows: {len(df):,}")
        for col in sorted(df.columns):
            column = df[col]
            parts.append(f"      - {col:25s} {str(column.dtype):12s} unique={column.nunique():<6d} sample={_sample_value(column, max_rows_sample)}")

    parts.append("")
    parts.append("STAR SCHEMA:")
    star = schema.get("star_schema", schema)
    ft = star["fact_table"]
    parts.append(f"  FACT TABLE: {ft['name']}")
    parts.append(f"    Measures: {ft['measures']}")
    parts.append(f"    FKs:      {ft.get('foreign_keys', [])}")

    for dname, ddef in star["dimension_tables"].items():
        parts.append(f"  DIM TABLE: {dname}")
        parts.append(f"    PK:          {ddef.get('surrogate_key', ddef.get('pk', 'N/A'))}")
        parts.append(f"    Hierarchy:   {ddef.get('hierarchy', ddef.get('levels', 'N/A'))}")
        parts.append(f"    Source:      {ddef.get('source_table', 'N/A')}")
        parts.append(f"    Columns:     {ddef.get('columns', ddef.get('levels', []))}")

    return "\n".join(parts)


def build_column_info(df: pd.DataFrame) -> str:
    """Build column-level info string for a single DataFrame (for LLM prompts)."""
    lines = []
    for col in df.columns:
        column = df[col]
        sample = column.dropna()
        sample_value = str(sample.iloc[0])[:40] if not sample.empty else "NULL"
        lines.append(f"  - {col:30s} dtype={str(column.dtype):12s} nulls={column.isna().sum():<6d} sample={sample_value}")
    return "\n".join(lines)
