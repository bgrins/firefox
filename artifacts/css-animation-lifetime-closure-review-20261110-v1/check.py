import argparse
import hashlib
import json
from pathlib import Path

BASE = Path(__file__).resolve().parent
ROOT = BASE.parents[1]


def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--out", type=Path, required=True)
    args = parser.parse_args()
    sources = json.loads((BASE / "SOURCES.json").read_text())
    held = json.loads((BASE / "HELD-SOURCES.json").read_text())
    refs = json.loads((BASE / "REFERENCES.json").read_text())
    for name, info in sources.items():
        assert digest(BASE / "source" / name) == info["sha256"], name
    for name, info in held.items():
        assert digest(BASE / "held-source" / name) == info["sha256"], name
    for name, sha in refs.items():
        assert digest(ROOT / name) == sha, name
    chunks = []
    excerpts = json.loads((BASE / "EXCERPTS.json").read_text())
    for item in excerpts:
        path = BASE / item["path"]
        assert digest(path) == item["source_sha256"]
        lo, hi = item["first_line"], item["last_line"]
        text = "\n".join(path.read_text().splitlines()[lo-1:hi]) + "\n"
        assert hashlib.sha256(text.encode()).hexdigest() == item["excerpt_sha256"]
        chunks.append(f"FILE {item['path']} LINES {lo}-{hi}\n" + text)
    assert (BASE / "EXCERPTS.txt").read_text() == "\n".join(chunks)
    scope = json.loads((BASE / "TRACE-SCOPE.json").read_text())
    analysis = json.loads((ROOT / scope["source"]).read_text())
    expected = []
    for episode in analysis["episodes"]:
        expected.append({"mode": episode["mode"], "task_masks": sorted({t["bits"] for t in episode["tasks"]}),
                         "tasks": len(episode["tasks"]), "initial_animation_only_tasks": len(episode["initial_animation_only_tasks"])})
    assert scope["episodes"] == expected
    assert all(not (int(mask) & (32 | 64 | 128)) for episode in expected for mask in episode["task_masks"])
    prefs = (BASE / "source/modules/libpref/init/StaticPrefList.yaml").read_text()
    pref = prefs.split("- name: layout.css.scroll-driven-animations.enabled\n", 1)[1].split("\n\n", 1)[0]
    assert "value: true" in pref
    result = {"result": "PASS", "source_snapshots": len(sources), "held_semantic_snapshots": len(held),
              "external_references": len(refs), "excerpts": len(excerpts), "trace_episodes": expected,
              "scroll_driven_animations_default": True, "browser_execution": False,
              "native_refinement": False, "termination_proof": False}
    args.out.write_text(json.dumps(result, indent=2) + "\n")
    print(json.dumps(result, indent=2))


if __name__ == "__main__":
    main()
