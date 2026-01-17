from __future__ import annotations

import re
import unicodedata
from datetime import datetime
from zoneinfo import ZoneInfo

import pandas as pd

DATE_TZ = 'Africa/Cairo'
DATE_FMT = '%d-%m-%Y'
TRUNC_LIMIT = 45


def normalize_text(x) -> str:
    if x is None:
        return ''
    if isinstance(x, float) and pd.isna(x):
        return ''
    s = str(x).replace('\u00A0', ' ')
    s = re.sub(r'\s+', ' ', s)
    return s.strip()


def strip_accents(s: str) -> str:
    return ''.join(c for c in unicodedata.normalize('NFD', s) if unicodedata.category(c) != 'Mn')


def norm_key(s: str) -> str:
    s = strip_accents(normalize_text(s).upper())
    s = re.sub(r'[^A-Z0-9]+', ' ', s)
    return s.strip()


def trunc(s: str, n: int = TRUNC_LIMIT) -> str:
    return normalize_text(s)[:n]


def today_str() -> str:
    try:
        return datetime.now(ZoneInfo(DATE_TZ)).strftime(DATE_FMT)
    except Exception:
        return datetime.now().strftime(DATE_FMT)


def only_digits(s: str) -> str:
    return re.sub(r'[^0-9]', '', s or '')
