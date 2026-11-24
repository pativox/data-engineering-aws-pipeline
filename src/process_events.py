from pathlib import Path
import json, csv
from datetime import datetime

ROOT = Path(__file__).resolve().parents[1]
SOURCE = ROOT / "data" / "incoming" / "events.json"
LANDING = ROOT / "data" / "landing"
CURATED = ROOT / "data" / "curated"
REJECTED = ROOT / "data" / "rejected"
REPORTS = ROOT / "reports"

REQUIRED = {"event_id","event_type","event_timestamp","customer_id","amount","source"}

def write_csv(path, rows, fields):
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w",newline="",encoding="utf-8") as f:
        w=csv.DictWriter(f,fieldnames=fields); w.writeheader(); w.writerows(rows)

def run():
    raw = json.loads(SOURCE.read_text(encoding="utf-8"))
    LANDING.mkdir(parents=True,exist_ok=True)
    (LANDING/"events_raw.json").write_text(json.dumps(raw,indent=2),encoding="utf-8")
    seen=set(); valid=[]; rejected=[]
    for event in raw:
        reason=None
        missing=REQUIRED-set(event)
        if missing: reason="missing_fields:" + ",".join(sorted(missing))
        elif event["event_id"] in seen: reason="duplicate_event_id"
        else: seen.add(event["event_id"])
        if not reason:
            try:
                datetime.fromisoformat(event["event_timestamp"].replace("Z","+00:00"))
                if float(event["amount"]) < 0: reason="negative_amount"
                if not str(event["customer_id"]).strip(): reason="empty_customer_id"
            except (ValueError, TypeError):
                reason="invalid_timestamp_or_amount"
        if reason:
            rejected.append({"event_id":event.get("event_id",""),"reason":reason})
        else:
            valid.append({
                "event_id":event["event_id"],"event_type":event["event_type"],
                "event_timestamp":event["event_timestamp"],"customer_id":event["customer_id"],
                "amount":round(float(event["amount"]),2),"source":event["source"]
            })
    fields=["event_id","event_type","event_timestamp","customer_id","amount","source"]
    write_csv(CURATED/"events_curated.csv",valid,fields)
    write_csv(REJECTED/"events_rejected.csv",rejected,["event_id","reason"])
    summary={
        "input_events":len(raw),"valid_events":len(valid),"rejected_events":len(rejected),
        "rejection_reasons":{},"idempotency_key":"event_id",
        "status":"PASS" if not rejected else "PASS_WITH_REJECTS",
        "generated_at_utc":datetime.utcnow().isoformat(timespec="seconds")
    }
    for r in rejected:
        summary["rejection_reasons"][r["reason"]]=summary["rejection_reasons"].get(r["reason"],0)+1
    REPORTS.mkdir(parents=True,exist_ok=True)
    (REPORTS/"run_summary.json").write_text(json.dumps(summary,indent=2),encoding="utf-8")
    print(json.dumps(summary,indent=2))

if __name__=="__main__":
    run()
