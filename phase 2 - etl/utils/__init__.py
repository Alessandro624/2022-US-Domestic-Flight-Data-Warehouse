from .config import *

try:
    from .llm_client import call_llm, LLM_PROVIDER
except ModuleNotFoundError:
    LLM_PROVIDER = None

    def call_llm(*args, **kwargs):
        raise RuntimeError("LLM client dependencies are not available in this environment.")


from .loader import load_tables
from .schema_guard import SchemaContract
from .dqa import DQAReport, run_dqa
from .domain_rules import get_domain_rules, WEATHER_VALIDITY_RULES
from .audit import AuditLog
from .cleaning import CleaningPipeline
from .etl_pipeline import ETLPipeline
from .schema_description import build_schema_description, build_column_info

try:
    from .missingness import MissingnessAnalyzer
except ModuleNotFoundError:
    MissingnessAnalyzer = None

try:
    from .outliers import OutlierDetector
except ModuleNotFoundError:
    OutlierDetector = None

__all__ = [
    "ANALYTICS_CONFIG",
    "AuditLog",
    "CLEANED_DATA_DIR",
    "CLEANED_PATHS",
    "CLEANING_REPORT_DIR",
    "COLUMN_DESCRIPTIONS",
    "DQAReport",
    "DQA_REPORT_DIR",
    "DW_DATA_DIR",
    "DW_PATHS",
    "DW_TABLE_MAP",
    "ETL_REPORT_DIR",
    "CleaningPipeline",
    "ETLPipeline",
    "LLM_PROVIDER",
    "MissingnessAnalyzer",
    "MISSING_REPORT_DIR",
    "MODELING_REPORT_DIR",
    "OutlierDetector",
    "ORIGINAL_DATA_DIR",
    "ORIGINAL_FILE_MAP",
    "ORIGINAL_FILES",
    "ORIGINAL_PATHS",
    "OLLAMA_BASE_URL",
    "OLLAMA_MODEL",
    "OUTLIER_REPORT_DIR",
    "PROJECT_ROOT",
    "RECONCILED_DATA_DIR",
    "RECONCILED_FILE_MAP",
    "RECONCILED_PATHS",
    "OUTPUT_ROOT",
    "SchemaContract",
    "WEATHER_COLS",
    "WEATHER_VALIDITY_RULES",
    "build_column_info",
    "build_schema_description",
    "call_llm",
    "get_domain_rules",
    "load_tables",
    "run_dqa",
]
