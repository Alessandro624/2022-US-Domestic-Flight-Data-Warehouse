from datetime import datetime
from dataclasses import dataclass
from typing import Any, Callable

import pandas as pd


@dataclass
class ETLStep:
    """A single step in the ETL pipeline."""

    name: str
    description: str
    timestamp: str = ""
    input_rows: int = 0
    output_rows: int = 0
    status: str = "pending"  # pending | running | done | error
    error_msg: str = ""


class ETLPipeline:
    """Lightweight ETL orchestrator with step logging."""

    def __init__(self, name: str = "ETL"):
        self.name = name
        self.steps: list[ETLStep] = []
        self.artifacts: dict = {}
        self.log_entries: list[dict] = []

    def run_step(self, step_name: str, func: Callable[..., Any], **kwargs: Any) -> Any:
        """Execute a function as a named ETL step with logging."""
        step = ETLStep(name=step_name, description=(func.__doc__ or "").strip())
        step.status = "running"
        step.timestamp = datetime.now().isoformat()
        print(f"\n[STEP] {step_name} ...", end=" ")
        try:
            result = func(**kwargs)
            step.status = "done"
            if isinstance(result, pd.DataFrame):
                step.output_rows = len(result)
            print(f"OK ({step.output_rows:,} rows)")
        except Exception as e:
            step.status = "error"
            step.error_msg = str(e)
            print(f"FAILED -- {e}")
            raise
        self.steps.append(step)
        return result

    def log_df(self, name: str, df: pd.DataFrame):
        """Store a DataFrame as a named artifact and log its shape."""
        self.artifacts[name] = df
        self.log_entries.append(
            {
                "artifact": name,
                "rows": len(df),
                "cols": len(df.columns),
                "timestamp": datetime.now().isoformat(),
            }
        )
        print(f"  [LOG] {name:<25} {len(df):>8,} rows x {len(df.columns):>3} cols")

    def summary(self) -> pd.DataFrame:
        """Return a summary DataFrame of all ETL steps."""
        return pd.DataFrame(
            [
                {
                    "step": s.name,
                    "description": s.description,
                    "status": s.status,
                    "input_rows": s.input_rows,
                    "output_rows": s.output_rows,
                    "timestamp": s.timestamp,
                    "error_msg": s.error_msg,
                }
                for s in self.steps
            ]
        )
