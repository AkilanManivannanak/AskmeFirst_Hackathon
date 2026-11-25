"""
Turn your latest live run into the offline demo backup.

    python record_demo.py            # uses the most recent complete run in runs/live.jsonl
    then set DEMO_MODE=1 in .env and restart the server

It follows ONE interview chain backwards from the latest plan (so other runs can't mix in) and
saves: the request, every question card, the plan and its revised versions, the draft preview and
the Pangram voice result. The previous demo is kept as demo_cache.backup.json.
"""
import json
import shutil
from pathlib import Path

ROOT = Path(__file__).resolve().parent
LOG = ROOT / "runs" / "live.jsonl"
OUT = ROOT / "demo_cache.json"

rows = [json.loads(l) for l in LOG.read_text().splitlines() if l.strip()]
first_plans = [i for i, r in enumerate(rows) if r["kind"] == "plan" and not r.get("change")]
if not first_plans:
    raise SystemExit("No plan found yet. Do one full live run to the plan screen first.")
p_idx = first_plans[-1]
request = rows[p_idx]["request"]

# walk backwards: question with history length n-1, n-2, ... 0, same request, each answer chain consistent
chain = []
want = None
for i in range(p_idx - 1, -1, -1):
    r = rows[i]
    if r["kind"] != "question" or r.get("request") != request or r["out"].get("done"):
        continue
    n = len(r.get("history") or [])
    if want is None or n == want:
        if chain and chain[0][1].get("history") and r["out"].get("question") != chain[0][1]["history"][-1]["question"]:
            continue  # belongs to a different run
        chain.insert(0, (i, r))
        want = n - 1
        if n == 0:
            break
if not chain or len(chain[0][1].get("history") or []) != 0:
    raise SystemExit("Could not find a complete interview for the latest plan. Do one full run, then try again.")
start = chain[0][0]

after = rows[p_idx:]
plans = [rows[p_idx]["out"]] + [r["out"] for r in after[1:] if r["kind"] == "plan" and r.get("request") == request and r.get("change")]
previews = [r for r in after if r["kind"] == "preview" and r.get("request") == request and r.get("markdown")]
voices = [r["out"] for r in rows[start:p_idx + 1] if r["kind"] == "voice"]

old = json.loads(OUT.read_text()) if OUT.exists() else {}
if OUT.exists():
    shutil.copy(OUT, ROOT / "demo_cache.backup.json")
demo = {
    "persona": "Recorded live run",
    "request": request,
    "upload_text": old.get("upload_text", ""),
    "questions": [{k: r["out"].get(k, "") for k in ("summary", "field", "question", "why", "suggestions")} for _, r in chain],
    "plans": [{k: v for k, v in p.items() if not k.startswith("_")} for p in plans],
    "preview": previews[-1]["markdown"] if previews else old.get("preview", ""),
    "voice_check": voices[-1] if voices else old.get("voice_check", {}),
}
OUT.write_text(json.dumps(demo, indent=2, ensure_ascii=False))
print(f"Saved demo for: {request!r}")
for q in demo["questions"]:
    print("   -", q["question"][:90])
print(f"  {len(demo['plans'])} plan version(s): {[p.get('title') for p in demo['plans']]}")
print(f"  preview: {'yes' if previews else 'kept old'}, Pangram voice: {'yes' if voices else 'kept old'}")
print("Check the list above is YOUR run. Then set DEMO_MODE=1 in .env and restart the server to replay it.")
