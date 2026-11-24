from pathlib import Path
from datetime import datetime, timezone
import csv, json

ROOT = Path(__file__).resolve().parents[1]
SOURCE = ROOT / "data/incoming/events.json"
REQUIRED = {"event_id", "event_type", "event_timestamp", "customer_id", "amount", "source"}

def write_csv(path, rows, fields):
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", newline="", encoding="utf-8") as stream:
        writer = csv.DictWriter(stream, fieldnames=fields)
        writer.writeheader()
        writer.writerows(rows)

def run():
    events = json.loads(SOURCE.read_text(encoding="utf-8"))
    landing = ROOT / "data/landing"
    landing.mkdir(parents=True, exist_ok=True)
    (landing / "events_raw.json").write_text(json.dumps(events, indent=2), encoding="utf-8")
    seen, valid, rejected = set(), [], []
    for event in events:
        missing = REQUIRED - event.keys()
        reason = None
        if missing:
            reason = "missing_fields:" + ",".join(sorted(missing))
        elif event["event_id"] in seen:
            reason = "duplicate_event_id"
        else:
            seen.add(event["event_id"])
        if reason is None:
            try:
                datetime.fromisoformat(event["event_timestamp"].replace("Z", "+00:00"))
                if float(event["amount"]) < 0:
                    reason = "negative_amount"
                if not str(event["customer_id"]).strip():
                    reason = "empty_customer_id"
            except (ValueError, TypeError):
                reason = "invalid_timestamp_or_amount"
        if reason:
            rejected.append({"event_id": event.get("event_id", ""), "reason": reason})
        else:
            valid.append({**event, "amount": round(float(event["amount"]), 2)})
    fields = ["event_id", "event_type", "event_timestamp", "customer_id", "amount", "source"]
    write_csv(ROOT / "data/curated/events_curated.csv", valid, fields)
    write_csv(ROOT / "data/rejected/events_rejected.csv", rejected, ["event_id", "reason"])
    summary = {"input_events": len(events), "valid_events": len(valid), "rejected_events": len(rejected),
               "idempotency_key": "event_id", "status": "PASS" if not rejected else "PASS_WITH_REJECTS"}
    (ROOT / "reports").mkdir(exist_ok=True)
    (ROOT / "reports/run_summary.json").write_text(json.dumps(summary, indent=2), encoding="utf-8")
    print(json.dumps(summary, indent=2))

if __name__ == "__main__":
    run()
