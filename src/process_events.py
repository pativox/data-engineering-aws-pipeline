"""Local event ingestion pipeline mirroring an S3 -> Lambda processing pattern."""
from pathlib import Path
import csv
import json
from datetime import datetime, timezone
from decimal import Decimal, InvalidOperation

ROOT = Path(__file__).resolve().parents[1]
SOURCE = ROOT / "data" / "incoming" / "events.json"
LANDING = ROOT / "data" / "landing"
CURATED = ROOT / "data" / "curated"
REJECTED = ROOT / "data" / "rejected"
REPORTS = ROOT / "reports"

REQUIRED = {"event_id", "event_type", "event_timestamp", "customer_id", "amount", "source"}
OUTPUT_FIELDS = ["event_id", "event_type", "event_timestamp", "customer_id", "amount", "source"]


def write_csv(path, rows, fields):
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=fields, extrasaction="ignore")
        writer.writeheader()
        writer.writerows(rows)


def transform_events(events):
    if not isinstance(events, list):
        raise ValueError("Input JSON must contain an array of events")

    seen, valid, rejected = set(), [], []
    for row_number, event in enumerate(events, start=1):
        if not isinstance(event, dict):
            rejected.append({"row_number": row_number, "event_id": "", "reason": "event_not_object"})
            continue

        missing = REQUIRED - set(event)
        reason = None
        event_id = str(event.get("event_id") or "").strip()
        if missing:
            reason = "missing_fields:" + ",".join(sorted(missing))
        elif not event_id or not str(event.get("event_type") or "").strip() or not str(event.get("source") or "").strip():
            reason = "empty_required_field"
        elif event_id in seen:
            reason = "duplicate_event_id"
        else:
            seen.add(event_id)

        try:
            timestamp = str(event.get("event_timestamp") or "").strip()
            datetime.fromisoformat(timestamp.replace("Z", "+00:00"))
            amount = Decimal(str(event.get("amount")).strip())
            if not amount.is_finite():
                raise InvalidOperation("amount must be finite")
            customer_id = str(event.get("customer_id") or "").strip()
            if not reason and amount < 0:
                reason = "negative_amount"
            if not reason and not customer_id:
                reason = "empty_customer_id"
        except (ValueError, TypeError, InvalidOperation):
            reason = reason or "invalid_timestamp_or_amount"

        if reason:
            rejected.append({"row_number": row_number, "event_id": event_id, "reason": reason})
            continue

        valid.append({
            "event_id": event_id,
            "event_type": str(event["event_type"]).strip(),
            "event_timestamp": timestamp,
            "customer_id": customer_id,
            "amount": str(amount.quantize(Decimal("0.01"))),
            "source": str(event["source"]).strip(),
        })
    return valid, rejected


def run():
    raw = json.loads(SOURCE.read_text(encoding="utf-8"))
    valid, rejected = transform_events(raw)

    LANDING.mkdir(parents=True, exist_ok=True)
    (LANDING / "events_raw.json").write_text(json.dumps(raw, indent=2), encoding="utf-8")
    write_csv(CURATED / "events_curated.csv", valid, OUTPUT_FIELDS)
    write_csv(REJECTED / "events_rejected.csv", rejected, ["row_number", "event_id", "reason"])

    reasons = {}
    for row in rejected:
        reasons[row["reason"]] = reasons.get(row["reason"], 0) + 1
    summary = {
        "input_events": len(raw),
        "valid_events": len(valid),
        "rejected_events": len(rejected),
        "rejection_reasons": reasons,
        "idempotency_key": "event_id",
        "status": "PASS" if not rejected else "PASS_WITH_REJECTS",
        "generated_at_utc": datetime.now(timezone.utc).isoformat(timespec="seconds"),
    }
    REPORTS.mkdir(parents=True, exist_ok=True)
    (REPORTS / "run_summary.json").write_text(json.dumps(summary, indent=2), encoding="utf-8")
    print(json.dumps(summary, indent=2))
    return summary


if __name__ == "__main__":
    run()
