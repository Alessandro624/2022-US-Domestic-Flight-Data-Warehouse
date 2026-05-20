import numpy as np
import pandas as pd
from .audit import AuditLog


class CleaningPipeline:
    """Modular data cleaning pipeline with integrated tracking and validation."""

    def __init__(self, df, table_name, pk_col=None):
        self.original = df.copy()
        self.df = df.copy()
        self.table_name = table_name
        self.pk_col = pk_col
        self.audit = AuditLog()
        self._steps = []
        self._dropped_obs_ids = set()

    def standardize_strings(self, cols, strip=True, title_case=False, upper=False):
        for col in cols:
            if col not in self.df.columns:
                continue
            before = self.df[col].copy()
            s = self.df[col].astype(str)
            if strip:
                s = s.str.strip()
            if title_case:
                s = s.str.title()
            if upper:
                s = s.str.upper()
            changed = (s != before.astype(str)) & before.notna()
            self.df.loc[changed, col] = s[changed]
            self.audit.log_batch("standardize_strings", col, changed, before, self.df[col], "Format string casing/spacing")
        self._steps.append("standardize_strings")
        return self

    def parse_dates(self, col, date_format="%Y-%m-%d"):
        if col not in self.df.columns:
            return self
        before = self.df[col].copy()
        parsed = pd.to_datetime(self.df[col], errors="coerce").dt.strftime(date_format)
        changed = (parsed != before.astype(str)) & before.notna()
        self.df.loc[changed, col] = parsed[changed]
        self.audit.log_batch("parse_dates", col, changed, before, self.df[col], f"Parsed to {date_format}")
        self._steps.append("parse_dates")
        return self

    def interpolate_temporal(
        self,
        cols,
        group_cols,
        date_col,
        hour_col,
        limit_direction="both",
        limit=None,
        max_gap_hours=None,
    ):
        """
        Interpolate numeric columns along the temporal axis within each group.
        Recommended values:
        - Weather observations: max_gap_hours=3, limit=2
        - Flight performance:   max_gap_hours=None, limit=None
        """
        if date_col not in self.df.columns or hour_col not in self.df.columns:
            return self

        if isinstance(group_cols, str):
            group_cols = [group_cols]
        group_cols = [c for c in group_cols if c in self.df.columns]
        target_cols = [c for c in cols if c in self.df.columns and pd.api.types.is_numeric_dtype(self.df[c])]
        if not target_cols:
            return self

        before_map = {col: self.df[col].copy() for col in target_cols}
        working = self.df.copy()
        working["_orig_idx"] = working.index
        working["_temporal_key"] = pd.to_datetime(working[date_col], errors="coerce") + pd.to_timedelta(pd.to_numeric(working[hour_col], errors="coerce"), unit="h")

        def _interpolate_group(group):
            group = group.copy()
            valid = group["_temporal_key"].notna()
            if valid.sum() < 2:
                return group

            interpolated = group.loc[valid, ["_orig_idx", "_temporal_key", *target_cols]].sort_values("_temporal_key").copy()
            interpolated = interpolated.set_index("_temporal_key")

            for col in target_cols:
                interpolated[col] = interpolated[col].interpolate(
                    method="time",
                    limit_direction=limit_direction,
                    limit=limit,
                )

                if max_gap_hours is not None:
                    originally_missing = group.loc[valid, col].isna()
                    originally_missing.index = interpolated.index

                    original_vals = group.loc[valid, ["_orig_idx", "_temporal_key", col]].copy()
                    original_vals = original_vals.set_index("_temporal_key")
                    non_missing_times = original_vals[col].dropna().index

                    if len(non_missing_times) >= 2:
                        filled_mask = originally_missing & interpolated[col].notna()
                        for fill_time in filled_mask[filled_mask].index:
                            earlier = non_missing_times[non_missing_times <= fill_time]
                            later = non_missing_times[non_missing_times >= fill_time]

                            dist_before = (fill_time - earlier[-1]).total_seconds() / 3600 if len(earlier) > 0 else float("inf")
                            dist_after = (later[0] - fill_time).total_seconds() / 3600 if len(later) > 0 else float("inf")

                            min_dist = min(dist_before, dist_after)
                            if min_dist > max_gap_hours:
                                interpolated.loc[fill_time, col] = np.nan

            group.loc[interpolated["_orig_idx"], target_cols] = interpolated[target_cols].to_numpy()
            return group

        if group_cols:
            updated = working.groupby(group_cols, dropna=False, sort=False, group_keys=False).apply(_interpolate_group)
        else:
            updated = _interpolate_group(working)

        updated = updated.sort_values("_orig_idx")
        for col in target_cols:
            after = pd.Series(updated[col].to_numpy(), index=updated["_orig_idx"]).reindex(self.df.index)
            changed = before_map[col].isna() & after.notna()
            self.df[col] = after.values
            if changed.any():
                constraint_msg = []
                if limit is not None:
                    constraint_msg.append(f"limit={limit} consecutive")
                if max_gap_hours is not None:
                    constraint_msg.append(f"max_gap={max_gap_hours}h")
                constraint_str = f" [{', '.join(constraint_msg)}]" if constraint_msg else ""

                self.audit.log_batch(
                    "interpolate_temporal",
                    col,
                    changed,
                    before_map[col],
                    self.df[col],
                    f"Interpolated by time within {group_cols or ['<entire table>']}{constraint_str}",
                )

        self._steps.append("interpolate_temporal")
        return self

    def round_discrete_cols(self, discrete_specs: dict) -> "CleaningPipeline":
        """
        Round numeric columns to the nearest valid discrete values specified in discrete_specs.
        """
        for col, valid_values in discrete_specs.items():
            if col not in self.df.columns:
                continue
            valid_arr = np.array(sorted(valid_values), dtype=float)
            before = self.df[col].copy()

            def _snap(x):
                if pd.isna(x):
                    return x
                idx = np.argmin(np.abs(valid_arr - float(x)))
                return valid_arr[idx]

            snapped = self.df[col].map(_snap)
            changed = snapped.notna() & before.notna() & (snapped != before)
            self.df[col] = snapped

            if changed.any():
                self.audit.log_batch(
                    "round_discrete_cols",
                    col,
                    changed,
                    before,
                    self.df[col],
                    f"Snap post-interpolation to valid domain {valid_values}",
                )
                print(f"  [round_discrete_cols] {col}: {int(changed.sum())} values snapped to domain {valid_values}")

        self._steps.append("round_discrete_cols")
        return self

    def handle_weather_nulls(
        self,
        weather_cols: list,
        flight_df: pd.DataFrame = None,
        obs_id_col: str = "obs_id",
        flight_fk_col: str = "weather_observation_id",
        cancelled_col: str = "cancelled",
        dangerous_cancellation_codes: list = None,
        max_dangerous_pct: float = 0.10,
        strategy: str = "auto",
    ) -> "CleaningPipeline":
        """
        Handle nulls in weather columns with different strategies: interpolate, drop and auto
        """
        if dangerous_cancellation_codes is None:
            dangerous_cancellation_codes = [1, 2]

        available_cols = [c for c in weather_cols if c in self.df.columns]
        if not available_cols:
            return self

        # AUTO
        if strategy == "auto":
            if flight_df is not None and obs_id_col in self.df.columns:
                from .missingness import MissingnessAnalyzer

                analyzer = MissingnessAnalyzer(self.df, self.table_name)
                result = analyzer.null_cooccurrence_flight_weather(
                    flight_df=flight_df,
                    weather_cols=available_cols,
                    obs_id_col=obs_id_col,
                    flight_fk_col=flight_fk_col,
                    cancelled_col=cancelled_col,
                    dangerous_cancellation_codes=dangerous_cancellation_codes,
                    max_dangerous_pct=max_dangerous_pct,
                )
                resolved = "drop" if result.get("safe_to_drop", False) else "interpolate"
                print(f"  [handle_weather_nulls] auto -> {resolved.upper()}")
                print(f"    co-occurrence: {result.get('perfect_cooccurrence')} | dangerous: {result.get('n_dangerous_cancellations')} | null rows: {result.get('n_null_weather_rows', 0):,}")
            else:
                resolved = "interpolate"
                print(f"  [handle_weather_nulls] auto -> INTERPOLATE (flight_df not provided or obs_id_col missing)")
        else:
            resolved = strategy

        # DROP
        if resolved == "drop":
            if obs_id_col not in self.df.columns:
                print(f"  [handle_weather_nulls] DROP skipped: '{obs_id_col}' not found.")
                return self

            null_mask = self.df[available_cols].isnull().all(axis=1)
            dropped_obs_ids = set(self.df.loc[null_mask, obs_id_col].dropna())
            n_before = len(self.df)
            self.df = self.df[~null_mask].reset_index(drop=True)
            n_dropped = n_before - len(self.df)

            # Save dropped
            self._dropped_obs_ids = dropped_obs_ids

            self.audit.log(
                "handle_weather_nulls_drop",
                str(available_cols),
                "batch",
                f"{n_before} rows",
                f"{len(self.df)} rows",
                f"Dropped {n_dropped} rows with all weather fields null",
            )
            print(f"  [handle_weather_nulls] DROP: {n_dropped:,} rows eliminated ({len(self.df):,} remaining). obs_ids removed: {len(dropped_obs_ids):,}")

            # Drop also the Flight rows linked, if flight_df provided
            if flight_df is not None and flight_fk_col in flight_df.columns and dropped_obs_ids:
                flight_mask = flight_df[flight_fk_col].isin(dropped_obs_ids)
                flight_df.drop(index=flight_df[flight_mask].index, inplace=True)
                flight_df.reset_index(drop=True, inplace=True)
                print(f"  [handle_weather_nulls] DROP flight rows linked: {int(flight_mask.sum()):,} rows eliminated ({len(flight_df):,} remaining).")

        # INTERPOLATE
        elif resolved == "interpolate":
            numeric_weather = [c for c in available_cols if c in self.df.columns and pd.api.types.is_numeric_dtype(self.df[c])]
            if numeric_weather:
                self.interpolate_temporal(
                    cols=numeric_weather,
                    group_cols=["origin_airport"] if "origin_airport" in self.df.columns else [],
                    date_col="obs_date" if "obs_date" in self.df.columns else "",
                    hour_col="obs_hour" if "obs_hour" in self.df.columns else "",
                    limit=2,
                    max_gap_hours=3,
                )
                _discrete_specs = {
                    c: ([0, 1] if c in ("low_level_cloud", "mid_level_cloud", "high_level_cloud") else [0, 1, 2, 3, 4])
                    for c in ["low_level_cloud", "mid_level_cloud", "high_level_cloud", "cloud_cover"]
                    if c in available_cols
                }
                if _discrete_specs:
                    self.round_discrete_cols(_discrete_specs)
            print(f"  [handle_weather_nulls] INTERPOLATE: columns {numeric_weather}")

        self._steps.append(f"handle_weather_nulls:{resolved}")
        return self

    def winsorize_numeric(self, cols, lower_pct=0.01, upper_pct=0.99):
        for col in cols:
            if col not in self.df.columns or not pd.api.types.is_numeric_dtype(self.df[col]):
                continue
            before = self.df[col].copy()
            lb = float(self.df[col].quantile(lower_pct))
            ub = float(self.df[col].quantile(upper_pct))
            capped = np.clip(self.df[col], lb, ub)
            changed = (capped != before) & before.notna()
            self.df.loc[changed, col] = capped[changed]
            self.audit.log_batch("winsorize_numeric", col, changed, before, self.df[col], f"Capped [{lower_pct}, {upper_pct}] lb={lb:.2f} ub={ub:.2f}")
        self._steps.append("winsorize_numeric")
        return self

    def deduplicate(self, natural_key_cols, keep="first"):
        before_len = len(self.df)
        dup_mask = self.df.duplicated(subset=natural_key_cols, keep=keep)
        n_dups = int(dup_mask.sum())
        self.df = self.df[~dup_mask].reset_index(drop=True)
        after_len = len(self.df)
        if n_dups > 0:
            self.audit.log("deduplicate", str(natural_key_cols), "batch", f"{before_len} rows", f"{after_len} rows", f"Removed {n_dups} duplicates")
        print(f"  [deduplicate] removed {n_dups} duplicates. {after_len} rows remain.")
        self._steps.append("deduplicate")
        return self

    def reset_serial_id(self, id_col):
        if id_col not in self.df.columns:
            return self
        self.df[id_col] = range(1, len(self.df) + 1)
        print(f"  [reset_serial_id] {id_col} reassigned 1..{len(self.df)}.")
        self._steps.append(f"reset_serial_id:{id_col}")
        return self

    def flag_invalid_tail_num(self, col="tail_num", pattern=r"^N[A-Z0-9]{2,5}$"):
        if col not in self.df.columns:
            return self
        before = self.df[col].copy()
        invalid = self.df[col].notna() & ~self.df[col].astype(str).str.match(pattern)
        self.df.loc[invalid, col] = np.nan
        self.audit.log_batch("flag_invalid_tail_num", col, invalid, before, self.df[col], "Set invalid N-number to NULL")
        if invalid.sum() > 0:
            print(f"  [flag_invalid_tail_num] {int(invalid.sum())} records set to NULL.")
        self._steps.append("flag_invalid_tail_num")
        return self

    def fix_invalid_to_null(self, col, valid_values, reason=""):
        if col not in self.df.columns:
            return self
        before = self.df[col].copy()
        invalid = self.df[col].notna() & ~self.df[col].isin(set(valid_values))
        if invalid.sum() > 0:
            self.df.loc[invalid, col] = np.nan
            self.audit.log_batch("fix_invalid_to_null", col, invalid, before, self.df[col], reason or "Value not in valid set -> NULL")
            print(f"  [fix_invalid_to_null:{col}] {int(invalid.sum())} values set to NULL.")
        self._steps.append(f"fix_invalid_to_null:{col}")
        return self

    def fix_fk_to_null(self, col, valid_keys, reason=""):
        if col not in self.df.columns:
            return self
        before = self.df[col].copy()
        broken = self.df[col].notna() & ~self.df[col].isin(set(valid_keys))
        if broken.sum() > 0:
            self.df.loc[broken, col] = np.nan
            self.audit.log_batch("fix_fk_to_null", col, broken, before, self.df[col], reason or "FK broken -> NULL")
            print(f"  [fix_fk_to_null:{col}] {int(broken.sum())} broken FK values set to NULL.")
        self._steps.append(f"fix_fk_to_null:{col}")
        return self

    def fix_weather_observation_fk(
        self,
        wo_df,
        flight_origin="origin",
        flight_date="fl_date",
        flight_hour="dep_hour",
        flight_fk="weather_observation_id",
        wo_airport="origin_airport",
        wo_date="obs_date",
        wo_hour="obs_hour",
        wo_id="obs_id",
    ):
        """Rebuilds weather_observation_id in Flight by joining on the natural key."""
        if not all(c in self.df.columns for c in [flight_origin, flight_date, flight_hour, flight_fk]):
            return self

        lookup = (
            wo_df[[wo_airport, wo_date, wo_hour, wo_id]]
            .dropna(subset=[wo_airport, wo_date, wo_hour])
            .drop_duplicates(subset=[wo_airport, wo_date, wo_hour])
            .rename(columns={wo_airport: flight_origin, wo_date: flight_date, wo_hour: flight_hour, wo_id: "_new_obs_id"})
        )

        self.df["_fl_date_str"] = pd.to_datetime(self.df[flight_date], errors="coerce").dt.strftime("%Y-%m-%d")
        lookup["_fl_date_str"] = pd.to_datetime(lookup[flight_date], errors="coerce").dt.strftime("%Y-%m-%d")
        lookup[flight_hour] = lookup[flight_hour].astype("Int64")
        self.df["_dep_hour_int"] = self.df[flight_hour].astype("Int64")

        merged = self.df[["_fl_date_str", flight_origin, "_dep_hour_int"]].merge(
            lookup.rename(columns={"_fl_date_str": "_fl_date_str", flight_hour: "_dep_hour_int"})[["_fl_date_str", flight_origin, "_dep_hour_int", "_new_obs_id"]],
            on=["_fl_date_str", flight_origin, "_dep_hour_int"],
            how="left",
        )

        before = self.df[flight_fk].copy()
        self.df[flight_fk] = merged["_new_obs_id"].values
        self.df.drop(columns=["_fl_date_str", "_dep_hour_int"], inplace=True)

        recovered = before.isna() & self.df[flight_fk].notna()
        nullified = before.notna() & self.df[flight_fk].isna()
        unchanged = self.df[flight_fk].notna().sum()
        print(f"  [fix_weather_observation_fk] recovered: {int(recovered.sum())} | nullified (no match): {int(nullified.sum())} | linked: {int(unchanged)}")
        self.audit.log(
            "fix_weather_observation_fk",
            flight_fk,
            "batch",
            f"before linked: {before.notna().sum()}",
            f"after linked: {self.df[flight_fk].notna().sum()}",
            "Rebuilt FK via natural key (origin, fl_date, dep_hour)",
        )
        self._steps.append("fix_weather_observation_fk")
        return self

    def fix_cancelled_air_time(self, cancelled_col="cancelled", air_time_col="air_time"):
        if cancelled_col not in self.df.columns or air_time_col not in self.df.columns:
            return self
        mask = (self.df[cancelled_col].fillna(0) > 0) & (self.df[air_time_col] > 0)
        before = self.df[air_time_col].copy()
        self.df.loc[mask, air_time_col] = np.nan
        self.audit.log_batch("fix_cancelled_air_time", air_time_col, mask, before, self.df[air_time_col], "Cancelled flight -> air_time NULL")
        if mask.sum() > 0:
            print(f"  [fix_cancelled_air_time] {int(mask.sum())} rows fixed.")
        self._steps.append("fix_cancelled_air_time")
        return self

    def fix_dew_point(self, temp_col="temperature", dew_col="dew_point"):
        if temp_col not in self.df.columns or dew_col not in self.df.columns:
            return self
        mask = (self.df[dew_col] > self.df[temp_col]) & self.df[dew_col].notna() & self.df[temp_col].notna()
        if mask.sum() > 0:
            d_before = self.df[dew_col].copy()
            self.df.loc[mask, [temp_col, dew_col]] = self.df.loc[mask, [dew_col, temp_col]].values
            self.audit.log_batch("fix_dew_point_swap", dew_col, mask, d_before, self.df[dew_col], "dew_point > temperature: swapped")
            print(f"  [fix_dew_point] {int(mask.sum())} rows swapped.")
        self._steps.append("fix_dew_point")
        return self

    def fix_wind_gust(self, spd_col="wind_spd", gust_col="wind_gust"):
        """Floors wind_gust to wind_spd when gust is below sustained wind."""
        if spd_col not in self.df.columns or gust_col not in self.df.columns:
            return self
        mask = self.df[gust_col].notna() & self.df[spd_col].notna() & (self.df[gust_col] < self.df[spd_col])
        if mask.sum() > 0:
            before = self.df[gust_col].copy()
            self.df.loc[mask, gust_col] = self.df.loc[mask, spd_col]
            self.audit.log_batch("fix_wind_gust_floor", gust_col, mask, before, self.df[gust_col], "wind_gust < wind_spd: floored to wind_spd")
            print(f"  [fix_wind_gust_floor] {int(mask.sum())} rows floored to the sustained wind speed.")
        self._steps.append("fix_wind_gust")
        return self

    def fix_cloud_cover_consistency(self, cover_col="cloud_cover", flag_cols=("low_level_cloud", "mid_level_cloud", "high_level_cloud"), layer_col="lowest_cloud_layer"):
        """If cloud_cover=0 but any layer flag is set or lowest_cloud_layer <= 10000 ft, correct cloud_cover to 1."""
        if cover_col not in self.df.columns:
            return self
        flag_active = pd.Series(False, index=self.df.index)
        for col in flag_cols:
            if col in self.df.columns:
                flag_active |= self.df[col].fillna(0.0) == 1.0
        if layer_col in self.df.columns:
            flag_active |= self.df[layer_col].notna() & (self.df[layer_col] <= 10_000)
        mask = (self.df[cover_col] == 0) & flag_active & self.df[cover_col].notna()
        if mask.sum() > 0:
            before = self.df[cover_col].copy()
            self.df.loc[mask, cover_col] = 1
            self.audit.log_batch("fix_cloud_cover_consistency", cover_col, mask, before, self.df[cover_col], "cloud_cover=0 but layer flags active -> set to 1 (few)")
            print(f"  [fix_cloud_cover_consistency] {int(mask.sum())} rows corrected.")
        self._steps.append("fix_cloud_cover_consistency")
        return self

    def fix_validity_range(self, col, min_val=None, max_val=None, fill=np.nan):
        if col not in self.df.columns:
            return self
        before = self.df[col].copy()
        mask = pd.Series(False, index=self.df.index)
        if min_val is not None:
            mask |= self.df[col] < min_val
        if max_val is not None:
            mask |= self.df[col] > max_val
        mask &= self.df[col].notna()
        if mask.sum() > 0:
            self.df.loc[mask, col] = fill
            self.audit.log_batch("fix_validity_range", col, mask, before, self.df[col], f"Out-of-range -> {fill}")
            print(f"  [fix_validity_range:{col}] {int(mask.sum())} values set to {fill}.")
        self._steps.append(f"fix_validity_range:{col}")
        return self

    @property
    def clean_df(self):
        return self.df.copy()
