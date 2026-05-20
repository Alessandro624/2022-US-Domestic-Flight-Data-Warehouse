import pandas as pd
import numpy as np
from sklearn.ensemble import IsolationForest
from sklearn.preprocessing import StandardScaler


def _safe_pct(flagged: int, total: int) -> float:
    if total <= 0:
        return 0.0
    return round(flagged / total * 100, 2)


class OutlierDetector:
    """
    Structured outlier detection for DW tables.
    Supports univariate (IQR, Modified Z-score) and
    multivariate (Isolation Forest) methods,
    plus consensus voting.
    """

    def __init__(self, df: pd.DataFrame, table_name: str):
        self.df = df.copy()
        self.table_name = table_name
        self._records = []
        self.outliers = pd.DataFrame(index=df.index)

    def detect_iqr(self, col: str, multiplier: float = 1.5):
        """IQR fence: flag rows where col < Q1 - k*IQR or > Q3 + k*IQR."""
        if col not in self.df.columns or self.df.empty:
            return self
        s = self.df[col].dropna()
        if s.empty:
            self.outliers[f"IQR_{col}"] = pd.Series(False, index=self.df.index)
            return self
        q1 = s.quantile(0.25)
        q3 = s.quantile(0.75)
        iqr = q3 - q1
        lo = q1 - multiplier * iqr
        hi = q3 + multiplier * iqr
        flag = ((self.df[col] < lo) | (self.df[col] > hi)).fillna(False)
        self.outliers[f"IQR_{col}"] = flag
        self._records.append(
            {
                "method": f"IQR (k={multiplier})",
                "column": col,
                "lower_fence": round(lo, 4),
                "upper_fence": round(hi, 4),
                "n_flagged": int(flag.sum()),
                "pct_flagged": _safe_pct(int(flag.sum()), len(self.df)),
            }
        )
        return self

    def detect_modified_zscore(self, col: str, threshold: float = 3.5):
        """Modified Z-score: robust to skewness (median-based)."""
        if col not in self.df.columns or self.df.empty:
            return self
        s = self.df[col].fillna(self.df[col].median())
        median = s.median()
        mad = np.median(np.abs(s - median))
        if mad == 0:
            return self
        mz = 0.6745 * (s - median) / mad
        flag = pd.Series(np.abs(mz) > threshold, index=self.df.index)
        self.outliers[f"ModZ_{col}"] = flag
        self._records.append(
            {
                "method": f"Modified Z-score (t={threshold})",
                "column": col,
                "lower_fence": None,
                "upper_fence": None,
                "n_flagged": int(flag.sum()),
                "pct_flagged": _safe_pct(int(flag.sum()), len(self.df)),
            }
        )
        return self

    def detect_isolation_forest(self, cols: list, contamination: float = 0.02):
        """Isolation Forest for multivariate anomaly detection."""
        available = [c for c in cols if c in self.df.columns]
        if len(available) < 2 or self.df.empty:
            return self
        X = self.df[available].fillna(self.df[available].median())
        if X.empty:
            return self
        X_sc = StandardScaler().fit_transform(X)
        preds = IsolationForest(contamination=contamination, random_state=42).fit_predict(X_sc)
        flag = pd.Series(preds == -1, index=self.df.index)
        self.outliers["IsoForest_Outlier"] = flag
        self._records.append(
            {
                "method": f"Isolation Forest (c={contamination})",
                "column": str(available),
                "lower_fence": None,
                "upper_fence": None,
                "n_flagged": int(flag.sum()),
                "pct_flagged": round(flag.sum() / len(self.df) * 100, 2),
            }
        )
        return self

    def consensus_vote(self, min_votes: int = 2) -> pd.Series:
        """
        Row-level consensus: True if flagged by at least min_votes methods.
        """
        if self.outliers.empty:
            return pd.Series(False, index=self.df.index)
        vote_count = self.outliers.sum(axis=1)
        return vote_count >= min_votes

    def flagged_rows(self, min_votes: int = 2) -> pd.DataFrame:
        """
        Return rows flagged as outliers by consensus, joined with their flags for inspection.
        """
        mask = self.consensus_vote(min_votes=min_votes)
        return self.df[mask].join(self.outliers[mask])

    def get_summary(self) -> pd.DataFrame:
        return pd.DataFrame(self._records)
