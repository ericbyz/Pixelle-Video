"""
API Usage Tracker - records and queries API call usage.

Data is persisted to a JSON file (data/usage_records.json).
Each record contains: timestamp, service, model, action, tokens, cost, etc.
"""

import json
import threading
from datetime import datetime, timezone
from pathlib import Path
from typing import Optional

from loguru import logger

# ---------------------------------------------------------------------------
# Pricing table (USD per 1M tokens / per call)
# ---------------------------------------------------------------------------

PRICING: dict[str, dict] = {
    # OpenAI
    "gpt-4o":         {"input": 2.50,  "output": 10.00, "unit": "per_1m_tokens"},
    "gpt-4o-mini":    {"input": 0.15,  "output": 0.60,  "unit": "per_1m_tokens"},
    "gpt-4.1":        {"input": 2.00,  "output": 8.00,  "unit": "per_1m_tokens"},
    "gpt-4.1-mini":   {"input": 0.40,  "output": 1.60,  "unit": "per_1m_tokens"},
    "gpt-4.1-nano":   {"input": 0.10,  "output": 0.40,  "unit": "per_1m_tokens"},
    "gpt-3.5-turbo":  {"input": 0.50,  "output": 1.50,  "unit": "per_1m_tokens"},
    # Anthropic
    "claude-sonnet-4-5":       {"input": 3.00,  "output": 15.00, "unit": "per_1m_tokens"},
    "claude-sonnet-4-6":       {"input": 3.00,  "output": 3.75,  "unit": "per_1m_tokens"},
    "claude-opus-4":           {"input": 15.00, "output": 75.00, "unit": "per_1m_tokens"},
    "claude-haiku-4":          {"input": 1.00,  "output": 5.00,  "unit": "per_1m_tokens"},
    "claude-3.5-sonnet":       {"input": 3.00,  "output": 15.00, "unit": "per_1m_tokens"},
    "claude-3-opus":           {"input": 15.00, "output": 75.00, "unit": "per_1m_tokens"},
    "claude-3-haiku":          {"input": 0.25,  "output": 1.25,  "unit": "per_1m_tokens"},
    # Alibaba Qwen
    "qwen-max":      {"input": 2.40,  "output": 9.60,  "unit": "per_1m_tokens"},
    "qwen-plus":     {"input": 0.80,  "output": 2.00,  "unit": "per_1m_tokens"},
    "qwen-turbo":    {"input": 0.30,  "output": 0.60,  "unit": "per_1m_tokens"},
    # DeepSeek
    "deepseek-chat": {"input": 0.27,  "output": 1.10,  "unit": "per_1m_tokens"},
    # Moonshot
    "moonshot-v1-8k":   {"input": 2.00, "output": 2.00,  "unit": "per_1m_tokens"},
    "moonshot-v1-32k":  {"input": 4.00, "output": 4.00,  "unit": "per_1m_tokens"},
    "moonshot-v1-128k": {"input": 8.00, "output": 8.00,  "unit": "per_1m_tokens"},
    # Google Gemini
    "gemini-2.5-pro":          {"input": 1.25,  "output": 10.00, "unit": "per_1m_tokens"},
    "gemini-2.5-flash":        {"input": 0.30,  "output": 0.60,  "unit": "per_1m_tokens"},
}

# Fallback pricing for unknown models (per 1M tokens)
DEFAULT_PRICING = {"input": 1.00, "output": 3.00, "unit": "per_1m_tokens"}


def estimate_cost(
    model: str,
    input_tokens: int = 0,
    output_tokens: int = 0,
) -> float:
    """Estimate cost in USD for a given model and token counts."""
    pricing = PRICING.get(model, DEFAULT_PRICING)
    if pricing["unit"] == "per_1m_tokens":
        return (input_tokens * pricing["input"] + output_tokens * pricing["output"]) / 1_000_000
    return 0.0


# ---------------------------------------------------------------------------
# Usage Tracker
# ---------------------------------------------------------------------------

class UsageTracker:
    """Thread-safe, file-persisted usage tracker."""

    def __init__(self, data_dir: Optional[str] = None):
        if data_dir is None:
            # Default: project_root/data/
            backend_dir = Path(__file__).resolve().parent.parent.parent  # new/
            project_root = backend_dir.parent / "old"
            data_dir = str(project_root / "data")
        self._data_dir = Path(data_dir)
        self._file = self._data_dir / "usage_records.json"
        self._lock = threading.Lock()

    # -- recording -----------------------------------------------------------

    def record(
        self,
        service: str,
        model: str,
        action: str,
        input_tokens: int = 0,
        output_tokens: int = 0,
        success: bool = True,
        error: str = "",
    ) -> dict:
        """Record a single API usage entry. Returns the record dict."""
        cost = estimate_cost(model, input_tokens, output_tokens)
        record = {
            "id": _nanoid(),
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "service": service,
            "model": model,
            "action": action,
            "input_tokens": input_tokens,
            "output_tokens": output_tokens,
            "cost": round(cost, 6),
            "success": success,
            "error": error,
        }
        with self._lock:
            self._append(record)
        return record

    # -- querying ------------------------------------------------------------

    def get_summary(self, days: int = 30) -> dict:
        """Return usage summary for the last N days."""
        records = self._read_all()
        if days > 0:
            cutoff = _days_ago(days)
            records = [r for r in records if r["timestamp"] >= cutoff]

        total_calls = len(records)
        total_input_tokens = sum(r.get("input_tokens", 0) for r in records)
        total_output_tokens = sum(r.get("output_tokens", 0) for r in records)
        total_cost = sum(r.get("cost", 0) for r in records)
        success_count = sum(1 for r in records if r.get("success", True))
        fail_count = total_calls - success_count

        # Breakdown by service
        by_service: dict[str, dict] = {}
        for r in records:
            svc = r["service"]
            if svc not in by_service:
                by_service[svc] = {"calls": 0, "input_tokens": 0, "output_tokens": 0, "cost": 0.0}
            by_service[svc]["calls"] += 1
            by_service[svc]["input_tokens"] += r.get("input_tokens", 0)
            by_service[svc]["output_tokens"] += r.get("output_tokens", 0)
            by_service[svc]["cost"] += r.get("cost", 0)

        # Breakdown by model
        by_model: dict[str, dict] = {}
        for r in records:
            mdl = r["model"]
            if mdl not in by_model:
                by_model[mdl] = {"calls": 0, "input_tokens": 0, "output_tokens": 0, "cost": 0.0, "service": r["service"]}
            by_model[mdl]["calls"] += 1
            by_model[mdl]["input_tokens"] += r.get("input_tokens", 0)
            by_model[mdl]["output_tokens"] += r.get("output_tokens", 0)
            by_model[mdl]["cost"] += r.get("cost", 0)

        # Breakdown by date (for chart)
        by_date: dict[str, dict] = {}
        for r in records:
            date_key = r["timestamp"][:10]  # YYYY-MM-DD
            if date_key not in by_date:
                by_date[date_key] = {"calls": 0, "cost": 0.0, "input_tokens": 0, "output_tokens": 0}
            by_date[date_key]["calls"] += 1
            by_date[date_key]["cost"] += r.get("cost", 0)
            by_date[date_key]["input_tokens"] += r.get("input_tokens", 0)
            by_date[date_key]["output_tokens"] += r.get("output_tokens", 0)

        return {
            "total_calls": total_calls,
            "success_count": success_count,
            "fail_count": fail_count,
            "total_input_tokens": total_input_tokens,
            "total_output_tokens": total_output_tokens,
            "total_cost": round(total_cost, 4),
            "by_service": by_service,
            "by_model": by_model,
            "by_date": by_date,
            "days": days,
        }

    def get_records(
        self,
        service: Optional[str] = None,
        model: Optional[str] = None,
        days: int = 30,
        page: int = 1,
        page_size: int = 50,
    ) -> dict:
        """Return paginated usage records with optional filters."""
        records = self._read_all()
        if days > 0:
            cutoff = _days_ago(days)
            records = [r for r in records if r["timestamp"] >= cutoff]
        if service:
            records = [r for r in records if r["service"] == service]
        if model:
            records = [r for r in records if r["model"] == model]

        # Sort by timestamp descending
        records.sort(key=lambda r: r["timestamp"], reverse=True)

        total = len(records)
        start = (page - 1) * page_size
        end = start + page_size
        page_records = records[start:end]

        return {
            "records": page_records,
            "total": total,
            "page": page,
            "page_size": page_size,
        }

    def get_models(self) -> list[dict]:
        """Return all models that have usage records."""
        records = self._read_all()
        seen: dict[str, dict] = {}
        for r in records:
            mdl = r["model"]
            if mdl not in seen:
                pricing = PRICING.get(mdl, DEFAULT_PRICING)
                seen[mdl] = {
                    "model": mdl,
                    "service": r["service"],
                    "input_price": pricing["input"],
                    "output_price": pricing["output"],
                    "unit": pricing["unit"],
                }
        return list(seen.values())

    def get_pricing(self) -> dict:
        """Return the full pricing table."""
        return PRICING

    # -- file I/O ------------------------------------------------------------

    def _append(self, record: dict):
        self._data_dir.mkdir(parents=True, exist_ok=True)
        records = self._read_all()
        records.append(record)
        # Keep last 10000 records to avoid unbounded growth
        if len(records) > 10000:
            records = records[-10000:]
        self._write_all(records)

    def _read_all(self) -> list[dict]:
        if not self._file.exists():
            return []
        try:
            with open(self._file, "r", encoding="utf-8") as f:
                return json.load(f)
        except (json.JSONDecodeError, IOError):
            return []

    def _write_all(self, records: list[dict]):
        with open(self._file, "w", encoding="utf-8") as f:
            json.dump(records, f, ensure_ascii=False)


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _nanoid() -> str:
    """Generate a short unique ID."""
    import random, string
    return "".join(random.choices(string.ascii_lowercase + string.digits, k=12))


def _days_ago(n: int) -> str:
    from datetime import timedelta
    cutoff = datetime.now(timezone.utc) - timedelta(days=n)
    return cutoff.isoformat()


# Singleton instance
usage_tracker = UsageTracker()


# ---------------------------------------------------------------------------
# Unified tracking API — decorator & context manager
# ---------------------------------------------------------------------------

import functools
from contextlib import asynccontextmanager


def track_api_call(service: str, action: str = "call", model_param: str = "model"):
    """
    Decorator: wrap any async service method to automatically record usage.

    Usage::

        @track_api_call("image", action="generate", model_param="workflow")
        async def __call__(self, prompt, workflow=None, **kw):
            ...

    The decorator extracts ``model`` from the wrapped method's ``model_param``
    keyword argument (falls back to positional-or-keyword with matching name,
    then to ``"unknown"``). On success it records ``success=True``; on
    exception it records ``success=False`` and re-raises.

    If the wrapped method returns an object that has ``input_tokens`` /
    ``output_tokens`` attributes (or dict keys), those are captured.
    """
    def decorator(fn):
        @functools.wraps(fn)
        async def wrapper(*args, **kwargs):
            # Resolve model name
            model = kwargs.get(model_param)
            if not model:
                model = "unknown"
            try:
                result = await fn(*args, **kwargs)
                in_tok = _extract_tokens(result, "input_tokens")
                out_tok = _extract_tokens(result, "output_tokens")
                usage_tracker.record(
                    service=service, model=str(model), action=action,
                    input_tokens=in_tok, output_tokens=out_tok,
                    success=True,
                )
                return result
            except Exception as e:
                usage_tracker.record(
                    service=service, model=str(model), action=action,
                    success=False, error=str(e),
                )
                raise
        return wrapper
    return decorator


@asynccontextmanager
async def tracked_call(service: str, model: str, action: str = "call"):
    """
    Async context manager for tracking a block of API code.

    Usage::

        async with tracked_call("video", "wan2.1", "generate"):
            result = await kit.execute(...)
    """
    try:
        yield
        usage_tracker.record(service=service, model=model, action=action, success=True)
    except Exception as e:
        usage_tracker.record(service=service, model=model, action=action, success=False, error=str(e))
        raise


def _extract_tokens(obj, key: str) -> int:
    """Try to pull token counts from a return value (attr or dict key)."""
    if obj is None:
        return 0
    val = getattr(obj, key, None)
    if val is None and isinstance(obj, dict):
        val = obj.get(key, 0)
    return int(val) if val else 0
