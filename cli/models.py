from enum import Enum
from typing import List, Optional, Dict
from pydantic import BaseModel


class AnalystType(str, Enum):
    MARKET = "market"
    MACRO_DATA = "macro_data"
    NEWS = "news"
    FUNDAMENTALS = "fundamentals"
