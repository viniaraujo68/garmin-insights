from datetime import date
from pathlib import Path
from zoneinfo import ZoneInfo

REPO_ROOT = Path(__file__).resolve().parents[3]
DATA_DIR = REPO_ROOT / "data"
RAW_DIR = DATA_DIR / "raw"
DB_PATH = DATA_DIR / "passada.db"
SITE_DIR = DATA_DIR / "site"
TOKEN_DIR = Path.home() / ".garminconnect"

TIMEZONE = ZoneInfo("America/Sao_Paulo")
HISTORY_START = date(2026, 7, 28)
LOOKBACK_DAYS = 3

PAUSE_SECONDS = 1.0
RETRY_WAIT_SECONDS = 90
MAX_ATTEMPTS = 3
RANGE_CHUNK_DAYS = 30
DETAIL_POINTS = 4000

RUNNING_TYPES = frozenset({"running", "treadmill_running", "trail_running", "track_running", "indoor_running", "street_running"})
FOOTBALL_TYPES = frozenset({"soccer", "football", "indoor_soccer", "futsal"})
STRENGTH_TYPES = frozenset({"strength_training"})
MORNING_READINESS_CONTEXT = "AFTER_WAKEUP_RESET"
PRIVACY_RADIUS_M = 400
ILLNESS_REFERENCE_FIRST_DAY = 30
ILLNESS_REFERENCE_LAST_DAY = 3
ILLNESS_MIN_REFERENCE_NIGHTS = 10
ILLNESS_Z = 2.0
