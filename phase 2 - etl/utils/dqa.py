import numpy as np
import pandas as pd


def _safe_score(issues: int, total: int) -> float:
    if total <= 0:
        return 0.0
    return 1 - (issues / total)


class DQAReport:
    """
    Data Quality Assessment Framework (ISO 25012).
    """

    def __init__(self, df: pd.DataFrame, table_name: str, primary_key: str = None):
        self.df = df.copy()
        self.table_name = table_name
        self.pk = primary_key
        self.results = {}
        self.flags = {}

    def check_completeness(self, required_cols: list = None):
        cols = required_cols or self.df.columns.tolist()
        missing_counts = self.df[cols].isnull().sum()
        total_values = len(self.df) * len(cols)
        total_missing = missing_counts.sum()
        score = _safe_score(int(total_missing), int(total_values))
        self.flags["completeness"] = self.df[cols].isnull().any(axis=1)
        self.results["completeness"] = {
            "score": round(score, 4),
            "issues": int(total_missing),
            "details": f"Missing per column: {missing_counts[missing_counts > 0].to_dict()}",
        }
        return self

    def check_uniqueness(self, key_cols: list = None):
        cols = key_cols or ([self.pk] if self.pk else self.df.columns.tolist())
        if not cols:
            self.flags["uniqueness"] = pd.Series(False, index=self.df.index)
            self.results["uniqueness"] = {"score": 0.0, "issues": 0, "details": "No key columns provided"}
            return self
        dup = self.df.duplicated(subset=cols, keep=False)
        score = _safe_score(int(dup.sum()), len(self.df))
        self.flags["uniqueness"] = dup
        self.results["uniqueness"] = {
            "score": round(score, 4),
            "issues": int(dup.sum()),
            "details": f"Duplicate rows on {cols}: {int(dup.sum())}",
        }
        return self

    def check_validity(self, rules: dict):
        all_invalid = pd.Series(False, index=self.df.index)
        rule_details = []
        for col, rule_fn in rules.items():
            if col not in self.df.columns:
                continue
            valid_mask = rule_fn(self.df[col]).fillna(False).astype(bool)
            invalid_mask = ~valid_mask & self.df[col].notna()
            all_invalid |= invalid_mask
            rule_details.append(f"{col}: {int(invalid_mask.sum())} invalid")
        score = _safe_score(int(all_invalid.sum()), len(self.df))
        self.flags["validity"] = all_invalid
        self.results["validity"] = {
            "score": round(score, 4),
            "issues": int(all_invalid.sum()),
            "details": " | ".join(rule_details),
        }
        return self

    def check_consistency(self, rules: list):
        all_inconsistent = pd.Series(False, index=self.df.index)
        for rule_fn in rules:
            all_inconsistent |= ~rule_fn(self.df)
        score = _safe_score(int(all_inconsistent.sum()), len(self.df))
        self.flags["consistency"] = all_inconsistent
        self.results["consistency"] = {
            "score": round(score, 4),
            "issues": int(all_inconsistent.sum()),
            "details": f"{int(all_inconsistent.sum())} rows violate rules",
        }
        return self

    def check_timeliness(self, date_col: str, max_age_days: int = 365, allow_future: bool = False):
        if date_col not in self.df.columns:
            return self
        now = pd.Timestamp.now()
        col = pd.to_datetime(self.df[date_col], errors="coerce")
        stale = (now - col).dt.days > max_age_days
        future = col > now if not allow_future else pd.Series(False, index=col.index)
        flag = stale | future
        score = _safe_score(int(flag.sum()), len(self.df))
        self.flags["timeliness"] = flag
        self.results["timeliness"] = {
            "score": round(score, 4),
            "issues": int(flag.sum()),
            "details": f"Future dates: {int(future.sum())} | Stale (>{max_age_days}d): {int(stale.sum())}",
        }
        return self

    def check_accuracy(self, tolerance_rules: dict):
        """
        Accuracy dimension: compare a column against a reference column
        within a tolerance.

        tolerance_rules: dict of {col: {"reference": ref_col, "tolerance": float}}
        Example: check that dep_hour matches the hour extracted from dep_time
        within +/-0.5 tolerance.
        """
        all_inaccurate = pd.Series(False, index=self.df.index)
        details = []
        for col, spec in tolerance_rules.items():
            ref_col = spec["reference"]
            tol = spec.get("tolerance", 0)
            if col not in self.df.columns or ref_col not in self.df.columns:
                continue
            diff = (self.df[col] - self.df[ref_col]).abs()
            inaccurate = (diff > tol) & self.df[col].notna() & self.df[ref_col].notna()
            all_inaccurate |= inaccurate
            details.append(f"{col} vs {ref_col} (tol={tol}): {int(inaccurate.sum())} inaccurate")
        if details:
            score = _safe_score(int(all_inaccurate.sum()), len(self.df))
            self.flags["accuracy"] = all_inaccurate
            self.results["accuracy"] = {
                "score": round(score, 4),
                "issues": int(all_inaccurate.sum()),
                "details": " | ".join(details),
            }
        return self

    def scorecard(self) -> pd.DataFrame:
        rows = []
        for dim, res in self.results.items():
            status = "PASS" if res["score"] >= 0.95 else ("WARN" if res["score"] >= 0.80 else "FAIL")
            rows.append(
                {
                    "Table": self.table_name,
                    "Dimension": dim.capitalize(),
                    "Score": res["score"],
                    "Issues": res["issues"],
                    "Status": status,
                    "Details": res["details"],
                }
            )
        return pd.DataFrame(rows)

    def overall_score(self) -> float:
        if not self.results:
            return 0.0
        return round(np.mean([v["score"] for v in self.results.values()]), 4)


def run_dqa(df, table_name, domain_rules, dfs_ref):
    """
    Run a full DQAReport on df using the shared domain_rules.
    """
    rules = domain_rules.get(table_name, {})
    pk = rules.get("pk")
    req_cols = rules.get("req_cols", df.columns.tolist())
    unique_keys = rules.get("unique_keys", [pk] if pk else None)
    validity = rules.get("validity", {})
    consistency_fns = rules.get("consistency", [])
    time_col = rules.get("time_col")

    dqa = DQAReport(df, table_name=table_name, primary_key=pk)
    dqa.check_completeness(required_cols=req_cols)
    dqa.check_uniqueness(key_cols=unique_keys)

    if validity:
        dqa.check_validity(validity)
    if consistency_fns:
        consistency_rules = [fn(dfs_ref) for fn in consistency_fns]
        dqa.check_consistency(consistency_rules)
    if time_col:
        dqa.check_timeliness(time_col, max_age_days=1825, allow_future=False)

    return dqa
