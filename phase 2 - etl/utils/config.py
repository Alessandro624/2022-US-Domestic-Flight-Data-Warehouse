from pathlib import Path

import numpy as np
import pandas as pd

try:
    import matplotlib.pyplot as plt
except ModuleNotFoundError:
    plt = None

pd.set_option("display.max_columns", None)
pd.set_option("display.float_format", lambda x: f"{x:.4f}")
np.random.seed(42)

PROJECT_ROOT = Path(__file__).resolve().parents[2]
DATA_ROOT = PROJECT_ROOT / "data"
OUTPUT_ROOT = PROJECT_ROOT / "output"

MATPLOTLIB_RCPARAMS = {
    "figure.facecolor": "#FAFAFA",
    "axes.facecolor": "#FAFAFA",
    "axes.spines.top": False,
    "axes.spines.right": False,
    "axes.grid": False,
    "font.size": 10,
}

if plt is not None:
    plt.rcParams.update(MATPLOTLIB_RCPARAMS)

ORIGINAL_DATA_DIR = DATA_ROOT / "1-original dataset"
RECONCILED_DATA_DIR = DATA_ROOT / "2-reconciled database"
CLEANED_DATA_DIR = DATA_ROOT / "3-cleaned database"
DW_DATA_DIR = DATA_ROOT / "4-data warehouse"

DQA_REPORT_DIR = OUTPUT_ROOT / "1-DQA"
MISSING_REPORT_DIR = OUTPUT_ROOT / "2-missing values"
OUTLIER_REPORT_DIR = OUTPUT_ROOT / "3-outliers"
CLEANING_REPORT_DIR = OUTPUT_ROOT / "4-cleaning pipeline"
MODELING_REPORT_DIR = OUTPUT_ROOT / "5-modeling"
ETL_REPORT_DIR = OUTPUT_ROOT / "6-ETL"

ORIGINAL_FILES = [
    "CompleteData.csv",
    "ActiveWeather.csv",
    "Cancellation.csv",
    "Carriers.csv",
    "Stations.csv",
]

RECONCILED_FILE_MAP = {
    "Flights": "Flights.csv",
    "Weather_Observations": "Weather_Observations.csv",
    "Aircrafts": "Aircrafts.csv",
    "Carriers": "Carriers.csv",
    "Stations": "Stations.csv",
    "Active_Weather": "Active_Weather.csv",
    "Cancellation": "Cancellation.csv",
}

RECONCILED_PATHS = {name: RECONCILED_DATA_DIR / fname for name, fname in RECONCILED_FILE_MAP.items()}

CLEANED_PATHS = {name: CLEANED_DATA_DIR / fname for name, fname in RECONCILED_FILE_MAP.items()}

COLUMN_DESCRIPTIONS = {
    "FL_DATE": "Date of flight",
    "DEP_HOUR": "Departure hour (0-23)",
    "MKT_UNIQUE_CARRIER": "Marketing Carrier Unique Code -> Carrier.Code",
    "MKT_CARRIER_FL_NUM": "Marketing Carrier Flight Number",
    "OP_UNIQUE_CARRIER": "Operating Carrier Unique Code -> Carrier.Code",
    "OP_CARRIER_FL_NUM": "Operating Carrier Flight Number",
    "TAIL_NUM": "FAA N-Number/Registration -> Aircraft.Tail_Num",
    "ORIGIN": "Origin airport code -> Station.Airport",
    "DEST": "Destination airport code -> Station.Airport",
    "DEP_TIME": "Actual departure timestamp",
    "CRS_DEP_TIME": "Scheduled departure timestamp (CRS)",
    "TAXI_OUT": "Taxi-out time (in minutes)",
    "DEP_DELAY": "Departure delay (in minutes; negative = early)",
    "AIR_TIME": "Wheels-off to wheels-on time (in minutes)",
    "DISTANCE": "Flight distance (in miles)",
    "CANCELLED": "Cancellation status -> Cancellation.Status",
    "WIND_DIR": "Wind direction (degrees)",
    "WIND_SPD": "Wind speed (in kt)",
    "WIND_GUST": "Wind gust speed (in kt)",
    "VISIBILITY": "Visibility (in miles)",
    "TEMPERATURE": "Temperature (in Celsius)",
    "DEW_POINT": "Dew point (in Celsius)",
    "REL_HUMIDITY": "Relative humidity (percentage)",
    "ALTIMETER": "Altimeter setting (in Hg)",
    "LOWEST_CLOUD_LAYER": "Height of lowest cloud layer (in ft)",
    "N_CLOUD_LAYER": "Number of cloud layers",
    "LOW_LEVEL_CLOUD": "Low-level cloud present (height below 6500 ft)",
    "MID_LEVEL_CLOUD": "Mid-level cloud present (between 6500 and 20000 ft)",
    "HIGH_LEVEL_CLOUD": "High-level cloud present (height above 20000 ft)",
    "CLOUD_COVER": "Cloud cover value",
    "ACTIVE_WEATHER": "Active weather condition -> Active_Weather.Status",
    "YEAR_OF_MANUFACTURE": "Year aircraft was manufactured",
    "MANUFACTURER": "Aircraft manufacturer name",
    "ICAO_TYPE": "ICAO aircraft type designator",
    "RANGE": "Encoded range category (Short/Medium/Long Range)",
    "WIDTH": "Aircraft body type (Narrow Body or Wide Body)",
    "AIRPORT_ID": "Internal numeric airport ID",
    "AIRPORT": "PK - Airport code (e.g., JFK)",
    "DISPLAY_AIRPORT_NAME": "Full airport name",
    "DISPLAY_AIRPORT_CITY_NAME_FULL": "Full city name",
    "AIRPORT_STATE_NAME": "Full state name",
    "AIRPORT_STATE_CODE": "State abbreviation",
    "LATITUDE": "Latitude coordinate",
    "LONGITUDE": "Longitude coordinate",
    "ELEVATION": "Elevation (in ft)",
    "ICAO": "ICAO airport code (UNIQUE)",
    "IATA": "IATA airport code (UNIQUE)",
    "FAA": "FAA identifier",
    "MESONET_STATION": "Mesonet station code (UNIQUE)",
    "STATUS": "Primary Key of the status",
    "WEATHER_DESCRIPTION": "Description of active weather condition",
    "CANCELLATION_REASON": "Reason for cancellation",
    "CODE": "PK - Carrier unique code",
    "DESCRIPTION": "Full carrier name or status description",
}

WEATHER_COLS = [
    "wind_dir",
    "wind_spd",
    "wind_gust",
    "visibility",
    "temperature",
    "dew_point",
    "rel_humidity",
    "altimeter",
    "lowest_cloud_layer",
    "n_cloud_layer",
    "low_level_cloud",
    "mid_level_cloud",
    "high_level_cloud",
    "cloud_cover",
    "active_weather",
]

ORIGINAL_WEATHER_COLS = [c.upper() for c in WEATHER_COLS]

ORIGINAL_FILE_MAP = {
    "CompleteData": "CompleteData.csv",
    "ActiveWeather": "ActiveWeather.csv",
    "Cancellation": "Cancellation.csv",
    "Carriers": "Carriers.csv",
    "Stations": "Stations.csv",
}

ORIGINAL_PATHS = {name: ORIGINAL_DATA_DIR / fname for name, fname in ORIGINAL_FILE_MAP.items()}

DW_TABLE_MAP = {
    "DIM_FL_DATES": "DIM_FL_DATES.csv",
    "DIM_DEP_HOURS": "DIM_DEP_HOURS.csv",
    "DIM_STATIONS": "DIM_STATIONS.csv",
    "DIM_CARRIERS": "DIM_CARRIERS.csv",
    "DIM_AIRCRAFTS": "DIM_AIRCRAFTS.csv",
    "DIM_JUNK": "DIM_JUNK.csv",
    "FLIGHTS": "FLIGHTS.csv",
}

DW_PATHS = {name: DW_DATA_DIR / fname for name, fname in DW_TABLE_MAP.items()}

LLM_PROVIDER = "ollama"  # Change to "openrouter" to use OpenRouter

# Ollama local configuration
OLLAMA_BASE_URL = "http://localhost:11434"
OLLAMA_MODEL = "llama3.1:8b"  # Run `ollama pull llama3.1:8b` first

# OpenRouter configuration
# Get your API key from https://openrouter.ai/keys
OPENROUTER_BASE_URL = "https://openrouter.ai/api/v1"
OPENROUTER_MODEL = "openrouter/free"

# Each table entry defines:
#   missing_target   : column whose missingness is tested
#   missing_features : predictors for MAR logistic test
#   mcar_pair        : (target_col, group_col) for chi-squared MCAR test
#   outlier_uni      : list of (column, iqr_multiplier) for univariate detection
#   outlier_multi    : list of columns for Isolation Forest
#   sample_size      : max rows to use (None = full table)
#
# IQR multiplier choices:
#   1.5 = standard (sensitive)
#   2.5 = tighter for physical sensor bounds
#   3.0 = wider for heavy-tailed distributions (dep_delay)
ANALYTICS_CONFIG = {
    "Flights": {
        "missing_target": "dep_delay",
        "missing_features": ["distance", "dep_hour", "air_time", "taxi_out"],
        "mcar_pair": ("dep_delay", "op_unique_carrier"),
        "outlier_uni": [
            ("dep_delay", 3.0),  # heavy-tailed: wider fence
            ("air_time", 1.5),
            ("taxi_out", 1.5),
        ],
        "outlier_multi": ["dep_delay", "air_time", "taxi_out"],
        "sample_size": 50_000,
    },
    "Weather_Observations": {
        "missing_target": "wind_gust",
        "missing_features": ["wind_spd", "visibility", "temperature", "rel_humidity"],
        "mcar_pair": ("wind_gust", "obs_hour"),
        "outlier_uni": [
            ("wind_gust", 2.5),
        ],
        "outlier_multi": ["wind_spd", "wind_gust", "temperature", "rel_humidity"],
        "sample_size": 30_000,
    },
    "Stations": {
        "missing_target": None,
        "missing_features": [],
        "mcar_pair": None,
        "outlier_uni": [],
        "outlier_multi": [],
        "sample_size": None,
    },
    "Aircrafts": {
        "missing_target": "year_of_manufacture",
        "missing_features": [],
        "mcar_pair": None,
        "outlier_uni": [],
        "outlier_multi": [],
        "sample_size": None,
    },
    "Carriers": {
        "missing_target": None,
        "missing_features": [],
        "mcar_pair": None,
        "outlier_uni": [],
        "outlier_multi": [],
        "sample_size": None,
    },
    "Active_Weather": {
        "missing_target": None,
        "missing_features": [],
        "mcar_pair": None,
        "outlier_uni": [],
        "outlier_multi": [],
        "sample_size": None,
    },
    "Cancellation": {
        "missing_target": None,
        "missing_features": [],
        "mcar_pair": None,
        "outlier_uni": [],
        "outlier_multi": [],
        "sample_size": None,
    },
}
