#!/usr/bin/env bash
# verify_stat_urls.sh — filter a fresh-stats JSON array down to stats whose source_url is live,
# non-redirecting, and not a login/paywall page. Fail-open: on any error a stat is DROPPED, never kept
# on a false positive; the script itself never hard-fails the run.
#
# Usage:
#   bash verify_stat_urls.sh '<json-array>'
#   echo '<json-array>' | bash verify_stat_urls.sh
#
# Input : JSON array of objects, each with at least {"source_url": "..."} (claim/value/year/source_name
#         are carried through unchanged). An "url" key is accepted as an alias for "source_url".
# Output: JSON object on stdout: {"kept":[...],"dropped":[{"url":..,"reason":..}],"summary":".."}
#
# Requires: python3 + curl (both standard on macOS).

set -uo pipefail

INPUT="${1:-}"
if [ -z "$INPUT" ]; then
  INPUT="$(cat)"
fi

python3 - "$INPUT" <<'PY'
import json, sys, subprocess, tempfile, os, re

raw = sys.argv[1] if len(sys.argv) > 1 else ""
try:
    stats = json.loads(raw) if raw.strip() else []
    if isinstance(stats, dict):
        stats = stats.get("fresh_stats") or stats.get("stats") or [stats]
    if not isinstance(stats, list):
        stats = []
except Exception as e:
    print(json.dumps({"kept": [], "dropped": [], "summary": "input parse error: %s" % e}))
    sys.exit(0)

PAYWALL = re.compile(
    r"(anmeldung erforderlich|bitte anmelden|jetzt anmelden|zum weiterlesen|"
    r"paywall|subscribe to (read|continue)|sign in to (read|continue)|"
    r"members only|log ?in to view|kostenpflichtig|premium-inhalt)",
    re.I,
)

def check(url):
    """Return (ok, reason). ok=True means keep."""
    if not url or not re.match(r"^https?://", url.strip(), re.I):
        return False, "no valid http(s) url"
    body = tempfile.NamedTemporaryFile(delete=False)
    body.close()
    try:
        # No -L: redirects are NOT followed, so a 3xx status surfaces as the code.
        code = subprocess.run(
            ["curl", "-s", "-A",
             "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36",
             "-o", body.name, "-w", "%{http_code}", "--max-time", "10", url],
            capture_output=True, text=True, timeout=25,
        ).stdout.strip()
    except Exception as e:
        try: os.unlink(body.name)
        except Exception: pass
        return False, "request failed: %s" % e
    try:
        with open(body.name, "rb") as fh:
            snippet = fh.read(20000).decode("utf-8", "ignore")
    except Exception:
        snippet = ""
    finally:
        try: os.unlink(body.name)
        except Exception: pass
    if not code.isdigit():
        return False, "no status (%r)" % code
    n = int(code)
    if 300 <= n < 400:
        return False, "redirect (%d)" % n
    if n >= 400 or n < 200:
        return False, "status %d" % n
    if PAYWALL.search(snippet):
        return False, "paywall/login markers"
    return True, "ok (%d)" % n

kept, dropped = [], []
for s in stats:
    url = ""
    if isinstance(s, dict):
        url = s.get("source_url") or s.get("url") or ""
    ok, reason = check(url)
    if ok:
        kept.append(s)
    else:
        dropped.append({"url": url, "reason": reason})

print(json.dumps({
    "kept": kept,
    "dropped": dropped,
    "summary": "%d/%d stats verified live; %d dropped" % (len(kept), len(stats), len(dropped)),
}, ensure_ascii=False, indent=2))
PY
