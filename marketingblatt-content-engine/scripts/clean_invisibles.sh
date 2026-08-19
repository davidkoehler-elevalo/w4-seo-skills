#!/usr/bin/env bash
# clean_invisibles.sh — Layer A hygiene pass over a finished postBody: strip invisible/format Unicode
# (zero-width, soft hyphen, word joiner, bidi controls, tag chars) and normalize exotic spaces.
# Deterministic and lossless for visible copy. Fail-open: if the cleaner is not installed the run
# continues and the report says so; the script itself never hard-fails the pipeline.
#
# Usage:
#   bash clean_invisibles.sh <file>              # rewrites <file> in place
#   bash clean_invisibles.sh <file> --report     # report only, writes nothing
#
# Input : a UTF-8 file holding the final postBody HTML (or any article markdown).
# Output: JSON object on stdout:
#         {"ok":true,"changed":N,"removed":{..},"replaced":{..},"nbsp_to_space":N,"summary":".."}
#
# HTML note: `&nbsp;` entities are untouched — only a LITERAL U+00A0 becomes a plain space. Use the
# entity in the body when a non-breaking space is intentional (German "25 %", "10 000", "CHF 1'200").
#
# Requires: python3 + the watermarks-remover clone (default ~/watermarks-remover, override with
# WATERMARKS_REMOVER_DIR). No HTTP service needed — this calls the library directly.

set -uo pipefail

FILE="${1:-}"
MODE="${2:-}"

if [ -z "$FILE" ]; then
  echo '{"ok":false,"reason":"no file given","summary":"usage: clean_invisibles.sh <file> [--report]"}'
  exit 0
fi

WR_DIR="${WATERMARKS_REMOVER_DIR:-$HOME/watermarks-remover}"

python3 - "$FILE" "$MODE" "$WR_DIR" <<'PY'
import json, sys, os, pathlib

path, mode, wr_dir = sys.argv[1], sys.argv[2], sys.argv[3]
report_only = mode == "--report"

def out(obj):
    print(json.dumps(obj, ensure_ascii=False, indent=2))
    sys.exit(0)

lib = pathlib.Path(wr_dir) / "service" / "scripts"
if not (lib / "text_unicode.py").exists():
    out({
        "ok": False,
        "reason": "watermarks-remover not found at %s" % wr_dir,
        "summary": "Layer A skipped — install the cleaner or set WATERMARKS_REMOVER_DIR. "
                   "Not a blocker; report it and continue.",
    })

sys.path.insert(0, str(lib))
try:
    from text_unicode import clean_text  # noqa: E402
except Exception as exc:  # pragma: no cover - defensive
    out({"ok": False, "reason": "import failed: %s" % exc,
         "summary": "Layer A skipped; not a blocker."})

try:
    original = pathlib.Path(path).read_text(encoding="utf-8")
except Exception as exc:
    out({"ok": False, "reason": "could not read %s: %s" % (path, exc),
         "summary": "Layer A skipped; not a blocker."})

# Defaults are deliberate: no NFKC (it rewrites typographic quotes), no aggressive homoglyph mapping,
# no emoji-glue stripping, no bidi stripping. Space normalization stays ON — a literal U+00A0 in
# model-written HTML is nearly always accidental, and `&nbsp;` remains available when it is not.
cleaned, stats = clean_text(original)

nbsp = stats.get("replaced", {}).get("U+00A0 NO-BREAK SPACE (Zs)", 0)
changed = stats.get("removed_count", 0) + stats.get("replaced_count", 0)

if changed and not report_only:
    tmp = pathlib.Path(path + ".tmp")
    tmp.write_text(cleaned, encoding="utf-8")
    os.replace(tmp, path)

if changed == 0:
    summary = "clean — no invisible Unicode found"
elif report_only:
    summary = "%d issue(s) found, nothing written (--report)" % changed
else:
    summary = "%d issue(s) fixed in %s" % (changed, os.path.basename(path))

out({
    "ok": True,
    "changed": changed,
    "removed": stats.get("removed", {}),
    "replaced": stats.get("replaced", {}),
    "nbsp_to_space": nbsp,
    "written": bool(changed) and not report_only,
    "summary": summary,
})
PY
