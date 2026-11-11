import hashlib
import json
from pathlib import Path
import subprocess

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]


def sha(data):
    return hashlib.sha256(data).hexdigest()


def read(name):
    return json.loads((HERE / name).read_text())


def main():
    sources = read("SOURCES.json")
    for name, expected in sources["files"].items():
        copied = (HERE / "source" / name).read_bytes()
        original = subprocess.check_output(["git", "-c", "core.fsmonitor=false", "show",
                                            sources["revision"] + ":" + name], cwd=ROOT)
        assert copied == original and sha(copied) == expected, name
    primary = read("PRIMARY.json")
    for name, record in primary.items():
        assert sha((HERE / "primary" / (name + ".html")).read_bytes()) == record["sha256"]
        assert record["indexed_sha"] == "hash:" + record["sha256"]
    for section, name in [("css-processing.json", "css-animations-2"),
                          ("scroll-keyframes.json", "scroll-animations-1"),
                          ("getkeyframes.json", "web-animations-1"),
                          ("wa-interface.json", "web-animations-1")]:
        assert read(section)["sha"] == "hash:" + primary[name]["sha256"]
    assert all(record["exit"] == 0 for record in read("ANCHORS.json").values())
    candidate = HERE.parent / "css-css-animation-keyframe-order-candidate-20261110-v1"
    old = (candidate / "source/layout/style/GeckoBindings.cpp").read_text()
    old_sources = json.loads((candidate / "SOURCES.json").read_text())
    assert sha(old.encode()) == old_sources["files"]["layout/style/GeckoBindings.cpp"]
    old_object = subprocess.check_output(["git", "-c", "core.fsmonitor=false", "show",
                                          old_sources["revision"] + ":layout/style/GeckoBindings.cpp"], cwd=ROOT)
    assert old.encode() == old_object
    current = (HERE / "source/layout/style/GeckoBindings.cpp").read_text()
    marker = "Keyframe* Gecko_GetOrCreateKeyframeForTimelineRangeOffset("
    end = "\nvoid Gecko_GetComputedURLSpec("
    def helper(text):
        return text[text.index(marker):text.index(end, text.index(marker))]
    assert helper(old) == helper(current)
    prior = "artifacts/css-css-animation-keyframe-failure-triage-20261110-v1/bug1778402.md"
    previous = subprocess.check_output(["git", "-c", "core.fsmonitor=false", "show",
                                        sources["revision"] + ":" + prior], cwd=ROOT)
    assert previous == (HERE / "bug1778402-prior.md").read_bytes()
    syntax = read("SYNTAX.json")
    assert syntax["html_sha256"] == sha((HERE / "proposal/named-range-group-earliest-order.html").read_bytes())
    assert syntax["exit"] == 0 and syntax["browser_execution"] is False
    assert read("ORDER-MODEL.json")["status"] == "pass"
    receipt = {"status": "pass", "source_revision": sources["revision"],
               "authenticated_native_test_metadata_files": len(sources["files"]),
               "primary_html_matches_index": True,
               "range_helper_unchanged_from_percentage_candidate_source": True,
               "range_helper_sha256": sha(helper(current).encode()),
               "prior_bug_context_sha256": sha(previous),
               "proposal_sha256": syntax["html_sha256"],
               "normative_verdict": "REACHED", "verdict_is_manually_reviewed": True,
               "browser_execution": False, "native_changes": False, "new_bug_count": 0}
    (HERE / "CHECK.json").write_text(json.dumps(receipt, indent=2) + "\n")
    print(json.dumps(receipt))


if __name__ == "__main__":
    main()
