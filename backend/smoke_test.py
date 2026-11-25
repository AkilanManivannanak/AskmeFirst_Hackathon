"""
Smoke test: one Hermes call, one Pangram call, one Reducto parse.
Run from backend/:   python smoke_test.py            (uses a generated test PDF)
                     python smoke_test.py old_flyer.jpg
Prints PASS/FAIL per service plus the raw shape of each response,
so we can fix field names in main.py before building on them.
"""

import os
import sys
import time
import traceback
from pathlib import Path

from dotenv import load_dotenv

ROOT = Path(__file__).resolve().parent
load_dotenv(ROOT / ".env", override=True)

results = {}


def section(name):
    print("\n" + "=" * 60 + f"\n{name}\n" + "=" * 60)


# ---------------- Hermes (Nous Portal) ----------------
def test_hermes():
    section("HERMES / AI PROVIDERS")
    from openai import OpenAI
    import json, re

    tested = False
    key = os.getenv("NOUS_API_KEY")
    if not key:
        print("NOUS_API_KEY is empty: skipping Hermes.")
    if key:
        client = OpenAI(api_key=key, base_url=os.getenv("NOUS_BASE_URL", "https://inference-api.nousresearch.com/v1"), timeout=25)
        ids = [m.id for m in client.models.list().data]
        print("Hermes models available:")
        for i in ids:
            print("  ", i)
        model = os.getenv("HERMES_INTERVIEW_MODEL", "auto")
        if model.lower() == "auto":
            lower = {i.lower(): i for i in ids}
            model = next((lower[p] for p in ["hermes-4.3-36b", "hermes-4-405b", "hermes-4-70b"] if p in lower), None) \
                or next((i for i in sorted(ids, reverse=True) if "hermes" in i.lower()), ids[0])
        _chat(client, model, "Hermes")
        tested = True
    okey = os.getenv("OPENAI_API_KEY")
    if okey:
        _chat(OpenAI(api_key=okey, base_url=os.getenv("OPENAI_BASE_URL") or None, timeout=25), os.getenv("OPENAI_MODEL", "gpt-4o-mini"), "Backup AI")
        tested = True
    akey = os.getenv("ANTHROPIC_API_KEY")
    if akey:
        import json as _j, re as _re, requests
        model = os.getenv("ANTHROPIC_MODEL", "claude-haiku-5-5")
        t = time.time()
        r = requests.post("https://api.anthropic.com/v1/messages", timeout=30,
                          headers={"x-api-key": akey, "anthropic-version": os.getenv("ANTHROPIC_VERSION", "2026-10-21"),
                                   "content-type": "application/json"},
                          json={"model": model, "max_tokens": 300,
                                "system": 'Reply with ONLY JSON: {"question": "...", "why": "..."}',
                                "messages": [{"role": "user", "content": 'They want: "a monthly budget for my family". Ask one plain question about who will use it.'}]})
        print(f"Claude: model={model} status={r.status_code} latency={time.time() - t:.1f}s")
        if r.status_code >= 400:
            raise RuntimeError(f"Claude error {r.status_code}: {r.text[:300]}")
        out = "".join(b.get("text", "") for b in r.json().get("content", []) if b.get("type") == "text")
        print("  output:", out[:300])
        _j.loads(_re.search(r"\{.*\}", out, flags=_re.S).group(0))
        print("  JSON parse: OK")
        tested = True
    if not tested:
        raise RuntimeError("No NOUS_API_KEY, OPENAI_API_KEY or ANTHROPIC_API_KEY in .env")


def _chat(client, model, label):
    import json, re
    t = time.time()
    resp = client.chat.completions.create(
        model=model, temperature=0.6, max_tokens=300,
        messages=[{"role": "system", "content": 'Reply with ONLY JSON: {"question": "...", "why": "..."}'},
                  {"role": "user", "content": 'They want: "a monthly budget for my family". Ask one plain question about who will use it.'}])
    out = resp.choices[0].message.content
    print(f"{label}: model={model} latency={time.time() - t:.1f}s")
    print("  output:", out[:300])
    cleaned = re.sub(r"<think>.*?</think>", "", out or "", flags=re.S)
    json.loads(re.search(r"\{.*\}", cleaned, flags=re.S).group(0))
    print("  JSON parse: OK")


# ---------------- Pangram ----------------
SAMPLE_TEXT = (
    "I run a small health workshop at the community center on Saturday mornings. "
    "Most of the people who come are older adults who were told by their doctor to watch "
    "their blood pressure but were never shown how. They feel rushed at appointments and "
    "embarrassed to ask basic questions. I want the flyer to feel friendly, not clinical, "
    "and to make it clear that nobody will be judged for what they eat or do not know yet."
)


def test_pangram():
    section("PANGRAM")
    key = os.getenv("PANGRAM_API_KEY")
    if not key:
        raise RuntimeError("PANGRAM_API_KEY missing in .env")
    print(f"Sample words: {len(SAMPLE_TEXT.split())}")
    try:
        from pangram import Pangram
    except ImportError as e:
        raise RuntimeError("pip install pangram-sdk  (import name may differ; check its README)") from e

    client = Pangram(api_key=key)
    t = time.time()
    try:
        r = client.predict(SAMPLE_TEXT, model="pangram-4")
    except TypeError:
        print("  predict() rejected model=, retrying without it")
        r = client.predict(SAMPLE_TEXT)
    print(f"latency: {time.time() - t:.1f}s")
    print("type:", type(r))
    print("raw:", repr(r)[:800])
    for k in ["prediction_short", "prediction", "fraction_ai", "fraction_human", "headline"]:
        v = r.get(k) if isinstance(r, dict) else getattr(r, k, None)
        print(f"  {k}: {v}")


# ---------------- Reducto ----------------
def make_test_pdf(path: Path):
    """Tiny valid PDF with flyer-like text, so the test needs no files."""
    lines = ["Free Health Workshop", "Saturday 10am, Community Center",
             "Learn to manage your blood pressure", "Bring your questions. Free tea."]
    ops = "BT /F1 16 Tf 60 740 Td " + " ".join(f"({l}) Tj 0 -24 Td" for l in lines) + " ET"
    stream = ops.encode()
    objs = [
        b"<< /Type /Catalog /Pages 2 0 R >>",
        b"<< /Type /Pages /Kids [3 0 R] /Count 1 >>",
        b"<< /Type /Page /Parent 2 0 R /MediaBox [0 0 612 792] /Contents 4 0 R "
        b"/Resources << /Font << /F1 5 0 R >> >> >>",
        b"<< /Length %d >>\nstream\n" % len(stream) + stream + b"\nendstream",
        b"<< /Type /Font /Subtype /Type1 /BaseFont /Helvetica >>",
    ]
    out = bytearray(b"%PDF-1.4\n")
    offsets = []
    for i, o in enumerate(objs, 1):
        offsets.append(len(out))
        out += b"%d 0 obj\n" % i + o + b"\nendobj\n"
    xref = len(out)
    out += b"xref\n0 %d\n0000000000 65535 f \n" % (len(objs) + 1)
    out += b"".join(b"%010d 00000 n \n" % off for off in offsets)
    out += b"trailer\n<< /Size %d /Root 1 0 R >>\nstartxref\n%d\n%%%%EOF\n" % (len(objs) + 1, xref)
    path.write_bytes(bytes(out))


def test_reducto(file_arg):
    section("REDUCTO")
    key = os.getenv("REDUCTO_API_KEY")
    if not key:
        raise RuntimeError("REDUCTO_API_KEY missing in .env")
    from reducto import Reducto

    path = Path(file_arg) if file_arg else ROOT / "test_flyer.pdf"
    if not file_arg:
        make_test_pdf(path)
    print("file:", path)

    client = Reducto(api_key=key)
    t = time.time()
    upload = client.upload(file=path)
    print("upload:", repr(upload)[:300])
    try:
        result = client.parse.run(input=upload.file_id)
    except TypeError:
        print("  parse.run(input=...) rejected, trying document_url=upload")
        result = client.parse.run(document_url=upload)
    print(f"latency: {time.time() - t:.1f}s")
    chunks = result.result.chunks
    print(f"chunks: {len(chunks)}")
    for c in chunks[:3]:
        print("---\n", c.content[:500])


# ---------------- run ----------------
if __name__ == "__main__":
    file_arg = sys.argv[1] if len(sys.argv) > 1 else None
    for name, fn in [("hermes", test_hermes), ("pangram", test_pangram),
                     ("reducto", lambda: test_reducto(file_arg))]:
        try:
            fn()
            results[name] = "PASS"
        except Exception as e:  # noqa: BLE001
            traceback.print_exc()
            results[name] = f"FAIL: {e}"

    section("SUMMARY")
    for k, v in results.items():
        print(f"  {k:8s} {v}")
