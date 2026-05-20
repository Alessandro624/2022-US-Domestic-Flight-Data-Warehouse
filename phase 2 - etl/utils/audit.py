from datetime import datetime
import pandas as pd


class AuditLog:
    """Records every cleaning transformation at the row and column level."""

    def __init__(self):
        self._entries = []

    def log(self, step, col, idx, before, after, reason=""):
        self._entries.append(
            {
                "step": step,
                "column": col,
                "row_index": idx,
                "before": before,
                "after": after,
                "reason": reason,
                "timestamp": datetime.now().isoformat(),
            }
        )

    def log_batch(self, step, col, mask, before_series, after_series, reason=""):
        for idx in mask[mask].index:
            self.log(
                step,
                col,
                idx,
                str(before_series.get(idx, "N/A")),
                str(after_series.get(idx, "N/A")),
                reason,
            )

    def to_df(self):
        return pd.DataFrame(self._entries)

    def summary(self):
        if not self._entries:
            return pd.DataFrame()
        df = self.to_df()
        return (
            df.groupby("step")
            .agg(
                changes=("row_index", "count"),
                cols_affected=("column", lambda x: ", ".join(x.unique())),
            )
            .reset_index()
            .sort_values("changes", ascending=False)
        )

    def __len__(self):
        return len(self._entries)
