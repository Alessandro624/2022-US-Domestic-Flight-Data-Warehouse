import pandas as pd


def _always_true(index):
    return pd.Series(True, index=index)


def _ref_keys(dfs, ref_table, ref_col):
    if dfs is None or ref_table not in dfs or ref_col not in dfs[ref_table].columns:
        return None
    return set(dfs[ref_table][ref_col].dropna().unique())


WEATHER_VALIDITY_RULES = {
    "wind_dir": lambda s: s.between(0, 360) | s.isna(),
    "wind_spd": lambda s: s.between(0, 250),
    "wind_gust": lambda s: s.between(0, 300),
    "visibility": lambda s: s.between(0, 20),
    "temperature": lambda s: s.between(-80, 60),
    "dew_point": lambda s: s.between(-80, 35),
    "rel_humidity": lambda s: s.between(0, 100),
    "altimeter": lambda s: s.between(25.0, 35.0),
    "lowest_cloud_layer": lambda s: s >= 0,
    "n_cloud_layer": lambda s: s >= 0,
    "low_level_cloud": lambda s: s.isin([0.0, 1.0]),
    "mid_level_cloud": lambda s: s.isin([0.0, 1.0]),
    "high_level_cloud": lambda s: s.isin([0.0, 1.0]),
    "cloud_cover": lambda s: s.isin([0, 1, 2, 3, 4]),
}


def get_domain_rules() -> dict:
    """
    Build the domain_rules dictionary.
    """

    def _flight_cancelled_no_airtime(dfs):
        """Cancelled flights must not have a positive air_time."""
        return lambda df: ~((df["cancelled"].fillna(0) > 0) & (df["air_time"] > 0))

    def _flight_dep_delay_present_if_not_cancelled(dfs):
        """dep_delay must be present for non-cancelled flights."""
        return lambda df: df["dep_delay"].notna() | (df["cancelled"].fillna(0) > 0)

    def _flight_air_time_positive_if_not_cancelled(dfs):
        """Non-cancelled flights with a recorded air_time must have air_time > 0."""
        return lambda df: (df["air_time"] > 0) | (df["cancelled"].fillna(0) > 0) | df["air_time"].isna()

    def _fk_check(fk_col, ref_table, ref_col):
        """
        Returns a closure that checks FK integrity of fk_col against
        ref_table[ref_col]. No-op when dfs_raw is absent or incomplete.
        """

        def factory(dfs):
            valid_keys = _ref_keys(dfs, ref_table, ref_col)
            if valid_keys is None:
                return lambda df: _always_true(df.index)
            return lambda df: df[fk_col].isin(valid_keys) | df[fk_col].isna()

        return factory

    def _dew_point_le_temperature(dfs):
        """Dew point must not exceed temperature."""
        return lambda df: ((df["dew_point"] <= df["temperature"]) | df["dew_point"].isna() | df["temperature"].isna())

    def _gust_ge_sustained(dfs):
        """Wind gust must be >= sustained wind speed when both are present."""
        return lambda df: ((df["wind_gust"] >= df["wind_spd"]) | df["wind_gust"].isna() | df["wind_spd"].isna())

    def _cloud_cover_clear_no_flags(dfs):
        """cloud_cover=0 (clear sky) must not have any layer flags active."""
        return lambda df: (
            (df["cloud_cover"] != 0)
            | df["cloud_cover"].isna()
            | ((df["low_level_cloud"].fillna(0.0) == 0.0) & (df["mid_level_cloud"].fillna(0.0) == 0.0) & (df["high_level_cloud"].fillna(0.0) == 0.0))
        )

    def _cloud_cover_clear_high_layer(dfs):
        """cloud_cover=0 must not have lowest_cloud_layer <= 10,000 ft."""
        return lambda df: ((df["cloud_cover"] != 0) | df["cloud_cover"].isna() | df["lowest_cloud_layer"].isna() | (df["lowest_cloud_layer"] > 10_000))

    def _wo_fk_active_weather(dfs):
        """active_weather_status must reference a valid Active_Weather.status value."""

        def rule(df):
            if dfs is None or "Active_Weather" not in dfs:
                return _always_true(df.index)
            valid = set(dfs["Active_Weather"]["status"].dropna().astype(float).unique())
            return df["active_weather_status"].isin(valid) | df["active_weather_status"].isna()

        return rule

    def _station_unique_airport_id(dfs):
        return lambda df: ~df["airport_id"].duplicated(keep=False) | df["airport_id"].isna()

    def _station_unique_icao(dfs):
        return lambda df: ~df["icao"].duplicated(keep=False) | df["icao"].isna()

    def _station_unique_iata(dfs):
        return lambda df: ~df["iata"].duplicated(keep=False) | df["iata"].isna()

    def _station_unique_mesonet(dfs):
        return lambda df: ~df["mesonet_station"].duplicated(keep=False) | df["mesonet_station"].isna()

    def _aircraft_wide_body_not_short_range(dfs):
        """Wide-body aircraft must not be classified as Short Range."""
        return lambda df: (~((df["width"] == "Wide-body") & (df["range"] == "Short Range")) | df["width"].isna() | df["range"].isna())

    domain_rules = {
        "Flights": {
            "pk": "flight_id",
            "unique_keys": ["fl_date", "dep_hour", "origin", "dest", "op_unique_carrier"],
            "req_cols": ["flight_id", "fl_date", "dep_hour", "origin", "dest", "op_unique_carrier"],
            "time_col": "fl_date",
            "validity": {
                "fl_date": lambda s: pd.to_datetime(s, errors="coerce").notna(),
                "dep_time": lambda s: pd.to_datetime(s, errors="coerce").notna(),
                "crs_dep_time": lambda s: pd.to_datetime(s, errors="coerce").notna(),
                "dep_hour": lambda s: s.between(0, 23),
                # Longest US domestic route: HNL-EWR about 4962 miles, add 10% buffer for detours
                "distance": lambda s: s.between(0, 5100),
                # Taxi-out: capped at 300 min (5 h) to filter sensor errors
                "taxi_out": lambda s: s.between(0, 300),
                # Air time: no US domestic exceeds 900 min
                "air_time": lambda s: s.between(0, 900),
                # Departure delay: allow up to 2 h early
                "dep_delay": lambda s: s >= -120,
            },
            "consistency": [
                _flight_cancelled_no_airtime,
                _flight_dep_delay_present_if_not_cancelled,
                _flight_air_time_positive_if_not_cancelled,
                _fk_check("origin", "Station", "airport"),
                _fk_check("dest", "Station", "airport"),
                _fk_check("tail_num", "Aircraft", "tail_num"),
                _fk_check("mkt_unique_carrier", "Carrier", "code"),
                _fk_check("op_unique_carrier", "Carrier", "code"),
                _fk_check("weather_observation_id", "Weather_Observation", "obs_id"),
                _fk_check("cancelled", "Cancellation", "status"),
            ],
        },
        "Weather_Observations": {
            "pk": "obs_id",
            "unique_keys": ["origin_airport", "obs_date", "obs_hour"],
            "req_cols": ["obs_id", "origin_airport", "obs_date", "obs_hour"],
            "time_col": "obs_date",
            "validity": {
                "obs_date": lambda s: pd.to_datetime(s, errors="coerce").notna(),
                "obs_hour": lambda s: s.between(0, 23),
                **{k: v for k, v in WEATHER_VALIDITY_RULES.items()},
            },
            "consistency": [
                _dew_point_le_temperature,
                _gust_ge_sustained,
                _cloud_cover_clear_no_flags,
                _cloud_cover_clear_high_layer,
                _fk_check("origin_airport", "Station", "airport"),
                _wo_fk_active_weather,
            ],
        },
        "Stations": {
            "pk": "airport",
            "unique_keys": ["airport"],
            "req_cols": ["airport", "airport_id", "display_airport_name", "latitude", "longitude"],
            "time_col": None,
            "validity": {
                "latitude": lambda s: s.between(-90, 90),
                "longitude": lambda s: s.between(-180, 180),
                "airport": lambda s: s.str.match(r"^[A-Z]{3}$"),
                "airport_state_code": lambda s: s.str.match(r"^[A-Z]{2}$"),
                "elevation": lambda s: s > -1500,
                "icao": lambda s: s.str.match(r"^[A-Z]{4}$"),
                "iata": lambda s: s.str.match(r"^[A-Z]{3}$"),
                "faa": lambda s: s.str.match(r"^[A-Z]{3}$"),
                "mesonet_station": lambda s: s.str.match(r"^[A-Z0-9]{3,5}$"),
            },
            "consistency": [
                _station_unique_airport_id,
                _station_unique_icao,
                _station_unique_iata,
                _station_unique_mesonet,
            ],
        },
        "Aircrafts": {
            "pk": "tail_num",
            "unique_keys": ["tail_num"],
            "req_cols": ["tail_num", "manufacturer", "year_of_manufacture"],
            "time_col": None,
            "validity": {
                "year_of_manufacture": lambda s: s.between(1950, pd.Timestamp.now().year),
                "tail_num": lambda s: s.str.match(r"^N[A-Z0-9]{4,5}$"),
                "manufacturer": lambda s: s.isin(["Airbus", "Boeing", "Bombardier", "Embraer", "Unknown"]),
                "icao_type": lambda s: s.isna() | s.str.match(r"^[A-Z0-9]{2,4}$"),
                "range": lambda s: s.isin(["Long Range", "Medium Range", "Short Range"]),
                "width": lambda s: s.isin(["Narrow-body", "Wide-body"]),
            },
            "consistency": [
                _aircraft_wide_body_not_short_range,
            ],
        },
        "Carriers": {
            "pk": "code",
            "unique_keys": ["code"],
            "req_cols": ["code", "description"],
            "time_col": None,
            "validity": {
                "code": lambda s: s.str.match(r"^[A-Z0-9]{2}$"),
            },
            "consistency": [],
        },
        "Active_Weather": {
            "pk": "status",
            "unique_keys": ["status"],
            "req_cols": ["status", "weather_description"],
            "time_col": None,
            "validity": {
                "status": lambda s: s.isin([0, 1, 2]),
            },
            "consistency": [],
        },
        "Cancellation": {
            "pk": "status",
            "unique_keys": ["status"],
            "req_cols": ["status", "cancellation_reason"],
            "time_col": None,
            "validity": {
                "status": lambda s: s.isin([0, 1, 2, 3, 4]),
            },
            "consistency": [],
        },
    }

    return domain_rules
