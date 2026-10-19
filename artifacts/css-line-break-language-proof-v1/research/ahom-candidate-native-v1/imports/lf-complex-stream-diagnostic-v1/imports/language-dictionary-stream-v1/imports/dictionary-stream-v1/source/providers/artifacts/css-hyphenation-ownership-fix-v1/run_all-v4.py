import hashlib
import json
import os
from pathlib import Path
import subprocess
import sys
from collections import Counter, defaultdict

ROOT = Path(__file__).resolve().parents[2]
HERE = Path(__file__).resolve().parent
phase = sys.argv[1]
assert phase == "all-candidate-v4"
receipt = HERE / (phase + "-receipt.json")
raw = HERE / (phase + ".jsonl")
log = HERE / (phase + ".log")
assert not any(p.exists() for p in (receipt, raw, log))
base = "testing/web-platform/tests/css/"
tests = ['testing/web-platform/tests/css/css-text/i18n/ja/css-text-line-break-ja-hyphens-normal.html', 'testing/web-platform/tests/css/css-text/i18n/ja/css-text-line-break-ja-hyphens-loose.html', 'testing/web-platform/tests/css/css-text/i18n/ja/css-text-line-break-ja-hyphens-strict.html', 'testing/web-platform/tests/css/css-text/i18n/zh/css-text-line-break-zh-hyphens-normal.html', 'testing/web-platform/tests/css/css-text/i18n/zh/css-text-line-break-zh-hyphens-loose.html', 'testing/web-platform/tests/css/css-text/i18n/zh/css-text-line-break-zh-hyphens-strict.html', 'testing/web-platform/tests/css/css-text/i18n/other-lang/css-text-line-break-de-hyphens-normal.html', 'testing/web-platform/tests/css/css-text/i18n/other-lang/css-text-line-break-de-hyphens-loose.html', 'testing/web-platform/tests/css/css-text/i18n/other-lang/css-text-line-break-de-hyphens-strict.html', 'testing/web-platform/tests/css/css-text/i18n/ja/css-text-line-break-ja-cpm-loose.html', 'testing/web-platform/tests/css/css-text/i18n/zh/css-text-line-break-zh-cpm-loose.html', 'testing/web-platform/tests/css/css-text/i18n/other-lang/css-text-line-break-de-cpm-loose.html', 'testing/web-platform/tests/css/css-text/hyphens/hyphenate-limit-chars-001.html', 'testing/web-platform/tests/css/css-text/hyphens/hyphens-span-001.html']
tests += ['testing/web-platform/tests/css/css-text/hyphens/hyphenate-limit-chars-dynamic.html', 'testing/web-platform/tests/css/css-text/line-break/line-break-language-text-partitions.html', 'testing/web-platform/tests/css/css-text/line-break/line-break-language-latin1-partitions.html']
tests += ['testing/web-platform/tests/css/css-text/hyphens/hyphenate-limit-chars-inline-ownership.html', 'testing/web-platform/tests/css/css-text/hyphens/hyphenate-limit-chars-pseudo-ownership.html']
paths = set(tests)
paths.update(['layout/generic/nsFirstLetterFrame.cpp', 'layout/generic/nsInlineFrame.cpp', 'servo/components/style/properties/data.py'])
absent = set()
paths.update(['layout/generic/nsTextFrame.cpp', 'layout/generic/nsTextFrame.h', 'layout/style/nsStyleStruct.h', 'layout/style/nsStyleStructInlines.h', 'layout/style/nsStyleStruct.cpp', 'dom/base/nsLineBreaker.cpp', 'dom/base/nsLineBreaker.h', 'intl/lwbrk/LineBreaker.cpp', 'intl/lwbrk/LineBreaker.h', 'gfx/thebes/gfxTextRun.cpp', 'gfx/thebes/gfxTextRun.h', 'layout/base/nsLayoutUtils.cpp', 'intl/hyphenation/glue/nsHyphenator.cpp', 'intl/hyphenation/glue/nsHyphenator.h', 'intl/lwbrk/LineBreakCache.h', 'third_party/rust/icu_segmenter/src/line.rs', 'third_party/rust/icu_segmenter/tests/css_line_break.rs', 'testing/web-platform/tests/config.json', 'objdir-full.noindex/dist/Nightly.app/Contents/MacOS/firefox', 'objdir-full.noindex/dist/Nightly.app/Contents/MacOS/XUL'])
paths.update(['intl/hyphenation/glue/nsHyphenationManager.cpp', 'intl/hyphenation/glue/nsHyphenationManager.h', 'intl/locales/en-US/hyphenation/hyph_en_US.hyf', 'objdir-full.noindex/dist/Nightly.app/Contents/Resources/hyphenation/hyph_en_US.hyf'])
paths.add(str(Path(__file__).relative_to(ROOT)))
import re
from html.parser import HTMLParser
from urllib.parse import urlsplit

class Resources(HTMLParser):
    def __init__(self):
        super().__init__()
        self.references = []

    def handle_starttag(self, tag, attributes):
        attrs = dict(attributes)
        if "src" in attrs:
            self.references.append(attrs["src"])
        if tag == "link" and set(attrs.get("rel", "").split()) & {"match", "mismatch", "stylesheet"}:
            if "href" in attrs:
                self.references.append(attrs["href"])

queue = list(tests)
seen = set()
while queue:
    name = queue.pop()
    if name in seen:
        continue
    seen.add(name)
    source = (ROOT / name).read_text()
    parser = Resources()
    parser.feed(source)
    references = parser.references + [m[1] for m in re.findall(r"url\(\s*([\"']?)([^)\"']+)\1\s*\)", source)]
    for ref in references:
        if urlsplit(ref).scheme or ref.startswith(("#", "//")):
            continue
        ref = urlsplit(ref).path
        target = (Path("testing/web-platform/tests") / ref.lstrip("/")
                  if ref.startswith("/") else Path(name).parent / ref)
        target = str((ROOT / target).resolve().relative_to(ROOT))
        assert (ROOT / target).is_file(), target
        paths.add(target)
        if target.endswith((".html", ".xht", ".svg", ".css")):
            queue.append(target)
for test in tests:
    meta = Path(test.replace("/tests/", "/meta/") + ".ini")
    (paths if (ROOT / meta).is_file() else absent).add(str(meta))
    for parent in meta.parents:
        if str(parent) == "testing/web-platform":
            break
        candidate = str(parent / "__dir__.ini")
        (paths if (ROOT / candidate).is_file() else absent).add(candidate)


def pins():
    return {p: hashlib.file_digest((ROOT / p).open("rb"), "sha256").hexdigest()
            for p in sorted(paths)}


before = pins()
sources = HERE / (phase + "-sources")
sources.mkdir()
for name in sorted(paths):
    if not name.startswith("objdir-") or name.endswith("hyph_en_US.hyf"):
        (sources / name.replace("/", "__")).write_bytes((ROOT / name).read_bytes())
command = ["/Users/bgrins/venvs/firefox/bin/python", "./mach", "wpt",
           "--binary", "objdir-full.noindex/dist/Nightly.app/Contents/MacOS/firefox",
           "--headless", "--processes=1", "--log-raw", str(raw), *tests]
record = {"phase": phase, "command": command, "pins_before": before,
          "absent_before": sorted(absent), "tests": tests}
(HERE / (phase + "-inputs.json")).write_text(json.dumps(record, indent=2) + "\n")
with log.open("w") as output:
    result = subprocess.run(command, cwd=ROOT, stdout=output,
                            stderr=subprocess.STDOUT,
                            env={**os.environ, "MOZ_SKIP_PATH_PERFORMANCE_CHECK": "1"})
after = pins()
rows = [json.loads(s) for s in raw.read_text().splitlines()] if raw.exists() else []
statuses = [r for r in rows if r.get("action") in ("test_status", "test_end")]
counts = defaultdict(Counter)
for row in statuses:
    counts[row["test"]][row["status"]] += 1
record.update({"exit_code": result.returncode, "pins_after": after,
               "all_inputs_unchanged": before == after,
               "absent_after": sorted(p for p in absent if not (ROOT / p).exists()),
               "counts": dict(counts), "statuses": statuses,
               "suite_end_count": sum(r.get("action") == "suite_end" for r in rows)})
receipt.write_text(json.dumps(record, indent=2) + "\n")
print(json.dumps({k: record[k] for k in ("phase", "exit_code", "all_inputs_unchanged", "counts", "suite_end_count")}, indent=2))
sys.exit(result.returncode if before == after and record["absent_after"] == record["absent_before"] else 2)
