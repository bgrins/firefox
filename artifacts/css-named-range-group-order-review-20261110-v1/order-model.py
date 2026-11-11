import json
from pathlib import Path


def build(source, rotate=False):
    frames, grouped = [], set()
    steps = []
    for key, value in reversed(source):
        matching = next((i for i, frame in enumerate(frames) if frame["key"] == key), None)
        if matching is None:
            frames.append({"key": key, "values": []})
            current = len(frames) - 1
        else:
            current = matching
            if rotate:
                frames.append(frames.pop(current))
                current = len(frames) - 1
            grouped.add(current)
        frames[current]["values"].append(value)
        steps.append({"visit": key, "frames": [f["key"] for f in frames], "saved_indices": sorted(grouped)})
    deduplicated = [frames[i]["key"] for i in sorted(grouped)]
    for index in grouped:
        frames[index]["values"] = frames[index]["values"][:1]
    return {"steps": steps, "deduplicated_groups": deduplicated, "output": list(reversed(frames))}


def main():
    named = build([("A", ".2"), ("B", "10px"), ("C", "20px"), ("B", "30px")])
    assert [f["key"] for f in named["output"]] == ["A", "C", "B"]
    assert next(f["values"] for f in named["output"] if f["key"] == "B") == ["30px"]
    existing = build([("entry0", "0"), ("entry100", "1"), ("contain0", ".8"), ("entry100", ".5")])
    assert [f["key"] for f in existing["output"]] == ["entry0", "contain0", "entry100"]
    unsafe = build([("A", "earlyA"), ("B", "earlyB"), ("C", "C"), ("B", "lateB"), ("A", "lateA")], rotate=True)
    assert [f["key"] for f in unsafe["output"]] == ["A", "B", "C"]
    assert unsafe["deduplicated_groups"] == ["A"]
    assert next(f["values"] for f in unsafe["output"] if f["key"] == "B") == ["lateB", "earlyB"]
    result = {"status": "pass", "named_equal_offset": named, "existing_wpt": existing,
              "naive_rotation_with_updated_current_index": unsafe,
              "finite_model_only": True, "native_execution": False, "kernel_proof": False}
    (Path(__file__).parent / "ORDER-MODEL.json").write_text(json.dumps(result, indent=2) + "\n")
    print("PASS: two source-order witnesses and one stale-index counterexample")


if __name__ == "__main__":
    main()
