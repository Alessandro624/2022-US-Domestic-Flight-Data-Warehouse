import pandas as pd
import numpy as np
from scipy.stats import chi2_contingency
from sklearn.preprocessing import StandardScaler
import statsmodels.api as sm


class MissingnessAnalyzer:
    """
    Structured analysis of missing value patterns and mechanisms.

    Classifies each column's missingness as:
    - MCAR : Missing Completely At Random (no relationship with observed data)
    - MAR  : Missing At Random (missingness predictable from other observed vars)
    - MNAR : Missing Not At Random (missingness depends on the unobserved value itself)

    Also detects temporal gap patterns in time-indexed data.
    """

    def __init__(self, df: pd.DataFrame, table_name: str):
        self.df = df.copy()
        self.table_name = table_name
        self.results = {}
        self._mechanism_classifications = {}

    def summary(self) -> pd.DataFrame:
        """Column-level missingness summary with qualitative status label."""
        miss = self.df.isnull().sum()
        total = len(self.df)
        pct = (miss / total * 100).round(2) if total > 0 else pd.Series(0.0, index=miss.index)
        result = pd.DataFrame(
            {
                "missing_count": miss,
                "missing_pct": pct,
                "present_count": total - miss,
                "dtype": self.df.dtypes,
            }
        )
        result["status"] = pd.cut(
            result["missing_pct"],
            bins=[-1, 0, 1, 5, 15, 100],
            labels=["complete", "negligible (<1%)", "low (1-5%)", "moderate (5-15%)", "high (>15%)"],
        )
        return result[result["missing_count"] > 0]

    def missing_correlation(self, target_col: str, features: list) -> pd.DataFrame:
        """
        Correlation between missingness indicator of target_col
        and numeric features.
        """
        available = [c for c in features if c in self.df.columns and pd.api.types.is_numeric_dtype(self.df[c])]
        if not available or target_col not in self.df.columns:
            return pd.DataFrame()
        miss_flag = self.df[target_col].isnull().astype(int)
        rows = []
        for col in available:
            corr = miss_flag.corr(self.df[col].fillna(self.df[col].median()))
            rows.append({"feature": col, "correlation_with_missingness": round(corr, 4)})
        return pd.DataFrame(rows).sort_values("correlation_with_missingness", key=abs, ascending=False)

    def missingness_correlation_matrix(self) -> pd.DataFrame:
        """
        Pairwise correlation between missingness indicators of all columns
        with missing values. Identifies columns that tend to be missing
        together (co-missingness).
        """
        miss_df = self.df.isnull().astype(int)
        cols_with_missing = miss_df.columns[miss_df.sum() > 0].tolist()
        if len(cols_with_missing) < 2:
            return pd.DataFrame()
        return miss_df[cols_with_missing].corr()

    def test_mcar_chi2(self, target_col: str, group_col: str) -> dict:
        """
        Chi-squared independence test.
        H0: missingness in target_col is independent of group_col (MCAR).
        Reject H0 -> evidence of MAR.
        """
        if target_col not in self.df.columns or group_col not in self.df.columns:
            return {"error": "column not found"}
        miss_flag = self.df[target_col].isnull().astype(int)
        group_vals = self.df[group_col].fillna("MISSING")
        ct = pd.crosstab(group_vals, miss_flag)
        chi2, p, dof, _ = chi2_contingency(ct)
        verdict = "Reject MCAR (MAR evidence)" if p < 0.05 else "Cannot reject MCAR"
        result = {
            "chi2": round(chi2, 4),
            "p_value": round(p, 6),
            "dof": dof,
            "significance": "***" if p < 0.001 else ("**" if p < 0.01 else ("*" if p < 0.05 else "ns")),
            "verdict": verdict,
        }
        self.results[f"mcar_{target_col}_{group_col}"] = result
        return result

    def test_mar_logistic(self, target_col: str, predictor_cols: list) -> dict:
        """
        Logistic regression: can missingness in target_col be predicted
        from predictor_cols? High pseudo-R2 -> MAR evidence.
        """
        available = [c for c in predictor_cols if c in self.df.columns]
        if not available or target_col not in self.df.columns:
            return {"error": "columns not found"}
        miss_flag = self.df[target_col].isnull().astype(int)
        if miss_flag.sum() < 10:
            return {"error": "too few missing values for logistic test"}
        X_raw = self.df[available].fillna(self.df[available].median())
        X = sm.add_constant(StandardScaler().fit_transform(X_raw))
        try:
            model = sm.Logit(miss_flag, X).fit(disp=False)
            pseudo_r2 = round(model.prsquared, 4)
        except Exception:
            pseudo_r2 = None
        verdict = "MAR evidence (missingness predictable)" if pseudo_r2 and pseudo_r2 > 0.05 else "Weak MAR signal"
        result = {"pseudo_r2": pseudo_r2, "predictors": available, "verdict": verdict}
        self.results[f"mar_{target_col}"] = result
        return result

    def null_cooccurrence_flight_weather(
        self,
        flight_df: pd.DataFrame,
        weather_cols: list,
        obs_id_col: str = "obs_id",
        flight_fk_col: str = "weather_observation_id",
        cancelled_col: str = "cancelled",
        dangerous_cancellation_codes: list = None,
        max_dangerous_pct: float = 0.10,
    ) -> dict:
        """
        Check if null values in weather columns correspond to the same rows in Flights table.
        If all weather fields are null for certain obs_ids, and those obs_ids correspond to flights,
        we can consider dropping those rows if they are not associated with a high rate of dangerous cancellations
        """
        if dangerous_cancellation_codes is None:
            dangerous_cancellation_codes = [1, 2]

        weather_df = self.df
        available_cols = [c for c in weather_cols if c in weather_df.columns]
        if not available_cols or obs_id_col not in weather_df.columns:
            return {"error": "Required columns missing from Weather_Observation"}

        # Weather rows where all weather fields are null
        weather_null_mask = weather_df[available_cols].isnull().all(axis=1)
        null_obs_ids = set(weather_df.loc[weather_null_mask, obs_id_col].dropna())
        n_null_weather_rows = int(weather_null_mask.sum())

        if flight_fk_col not in flight_df.columns:
            return {"error": f"Column '{flight_fk_col}' not found in flight_df"}

        # Flights that point to obs_ids with all weather fields null
        affected_flights = flight_df[flight_df[flight_fk_col].isin(null_obs_ids)]
        n_affected_flights = len(affected_flights)

        # Dangerous cancellations among the affected flights
        if cancelled_col in affected_flights.columns:
            n_dangerous = int(affected_flights[cancelled_col].isin(dangerous_cancellation_codes).sum())
            dangerous_pct = round(n_dangerous / n_affected_flights, 4) if n_affected_flights > 0 else 0.0
        else:
            n_dangerous = -1  # column absent, we cannot verify
            dangerous_pct = None

        perfect_cooccurrence = (n_null_weather_rows == n_affected_flights) and (n_null_weather_rows > 0)

        dangerous_within_threshold = (dangerous_pct is not None) and (dangerous_pct <= max_dangerous_pct)
        safe_to_drop = perfect_cooccurrence and (n_dangerous == 0 or dangerous_within_threshold)

        if not perfect_cooccurrence:
            reason = "imperfect co-occurrence"
        elif not dangerous_within_threshold and n_dangerous > 0:
            reason = f"dangerous cancellations {dangerous_pct:.1%} > threshold {max_dangerous_pct:.1%} — " f"consider raising max_dangerous_pct or inspecting the {n_dangerous} flights"
        else:
            reason = "ok"

        return {
            "n_null_weather_rows": n_null_weather_rows,
            "n_affected_flights": n_affected_flights,
            "perfect_cooccurrence": perfect_cooccurrence,
            "n_dangerous_cancellations": n_dangerous,
            "dangerous_pct": dangerous_pct,
            "max_dangerous_pct_threshold": max_dangerous_pct,
            "safe_to_drop": safe_to_drop,
            "reason": reason,
            "recommendation": ("SAFE TO DROP - delete rows with null weather fields and corresponding flights" if safe_to_drop else f"INTERPOLATE — {reason}"),
        }

    def classify_mechanism(
        self,
        target_col: str,
        group_cols: list = None,
        predictor_cols: list = None,
    ) -> dict:
        """
        Classify the missingness mechanism of a single column.

        Decision logic:
        1. If chi-squared cannot reject MCAR -> MCAR
        2. If logistic regression has pseudo-R2 > 0.05 -> MAR
        3. If high missingness correlation with specific predictors -> MAR
        4. If neither MCAR nor MAR -> MNAR (default for systematically
           missing values, e.g. wind_gust not reported in calm conditions)
        """
        if target_col not in self.df.columns:
            return {"error": "column not found"}

        miss_pct = self.df[target_col].isna().mean()
        if miss_pct == 0:
            return {"mechanism": "COMPLETE", "confidence": 1.0, "details": "No missing values"}

        # Step 1: MCAR test
        mcar_verdict = "Cannot reject MCAR"
        if group_cols:
            for gc in group_cols:
                if gc in self.df.columns:
                    r = self.test_mcar_chi2(target_col, gc)
                    if "verdict" in r:
                        mcar_verdict = r["verdict"]
                        break

        # Step 2: MAR test
        mar_evidence = False
        mar_r2 = None
        if predictor_cols:
            r = self.test_mar_logistic(target_col, predictor_cols)
            if "pseudo_r2" in r and r["pseudo_r2"] is not None:
                mar_r2 = r["pseudo_r2"]
                mar_evidence = mar_r2 > 0.05

        # Step 3: Classify
        if mcar_verdict == "Cannot reject MCAR" and not mar_evidence:
            mechanism = "MCAR"
            confidence = 0.7
        elif mar_evidence:
            mechanism = "MAR"
            confidence = min(mar_r2 / 0.3, 1.0) if mar_r2 else 0.5
        else:
            mechanism = "MNAR"
            confidence = 0.6
            details_note = (
                "Missingness may depend on the unobserved value itself. "
                "Common in weather data (e.g., wind_gust not reported when calm, "
                "ceiling not reported when sky clear). Domain knowledge required."
            )

        result = {
            "mechanism": mechanism,
            "confidence": round(confidence, 2),
            "missing_pct": round(miss_pct * 100, 2),
            "mcar_test": mcar_verdict,
            "mar_pseudo_r2": mar_r2,
        }
        if mechanism == "MNAR":
            result["details"] = details_note

        self._mechanism_classifications[target_col] = result
        return result

    def classify_all(
        self,
        config: dict = None,
    ) -> pd.DataFrame:
        """
        Classify missingness mechanism for all columns with missing values.
        """
        config = config or {}
        missing_cols = self.df.columns[self.df.isnull().any()].tolist()
        results = []
        for col in missing_cols:
            col_config = config.get(col, {})
            r = self.classify_mechanism(
                col,
                group_cols=col_config.get("group_cols"),
                predictor_cols=col_config.get("predictor_cols"),
            )
            if "error" not in r:
                results.append({"column": col, **r})

        return pd.DataFrame(results) if results else pd.DataFrame()

    def detect_temporal_gaps(
        self,
        date_col: str,
        hour_col: str = None,
        group_col: str = None,
        expected_freq: str = "h",
    ) -> pd.DataFrame:
        """
        Detect temporal gaps in time-indexed data.
        """
        df = self.df.copy()
        dates = pd.to_datetime(df[date_col], errors="coerce")
        if hour_col and hour_col in df.columns:
            dates = dates + pd.to_timedelta(pd.to_numeric(df[hour_col], errors="coerce"), unit="h")

        df["_ts"] = dates
        df = df.dropna(subset=["_ts"]).sort_values("_ts")

        gap_records = []

        def _find_gaps(group_df):
            group_records = []
            ts = group_df["_ts"].sort_values().unique()
            if len(ts) < 2:
                return group_records
            ts_series = pd.Series(ts)
            diffs = ts_series.diff()
            expected = pd.Timedelta(1, unit=expected_freq)
            for i in range(1, len(ts_series)):
                gap = diffs.iloc[i]
                if gap > expected * 1.5:
                    group_records.append(
                        {
                            "gap_start": ts_series.iloc[i - 1],
                            "gap_end": ts_series.iloc[i],
                            "gap_length_hours": gap.total_seconds() / 3600,
                            "gap_length_intervals": int(gap / expected),
                        }
                    )
            return group_records

        if group_col and group_col in df.columns:
            for name, group in df.groupby(group_col, dropna=False):
                group_records = _find_gaps(group)
                for rec in group_records:
                    rec[group_col] = name
                gap_records.extend(group_records)
        else:
            gap_records.extend(_find_gaps(df))

        return pd.DataFrame(gap_records)
