import copy
import hashlib
import json
from pathlib import Path
from materialize import materialize

BASE = Path(__file__).resolve().parent
ROOT = BASE.parents[1]


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def validate(record, sources):
    if set(sources) != {"old-generic.rs", "current-generic.rs", "animated.rs"}:
        raise ValueError("Snapshot inventory")
    for name, source in sources.items():
        if hashlib.sha256(source.encode()).hexdigest() != record["sha256"][name]:
            raise ValueError("Snapshot bytes: " + name)
    old, current, animated = (sources[n] for n in ("old-generic.rs", "current-generic.rs", "animated.rs"))
    if old.count(record["old_arm"]) != 1 or old.replace(record["old_arm"], record["new_arm"], 1) != current:
        raise ValueError("Exact patch")
    snippets = [
        (current, "InterpolateMatrix { .. } | AccumulateMatrix { .. } => return Err(()),"),
        (current, "let matrix = operation.to_3d_matrix(reference_box)?;"),
        (current, "transform = matrix.then(&transform);"),
        (animated, "Transform::components_to_transform_3d_matrix(left, None)?"),
        (animated, "Transform::components_to_transform_3d_matrix(right, None)?"),
        (animated, "let from_list = Transform(left.to_vec().into());"),
        (animated, "let to_list = Transform(right.to_vec().into());"),
        (animated, "Matrix3D::from(left).animate(&Matrix3D::from(right), procedure)?"),
    ]
    for source, token in snippets:
        if source.count(token) != 1:
            raise ValueError("Bridge token: " + token)


def run(live):
    record = materialize()
    sources = {name: (BASE / name).read_text() for name in record["sha256"]}
    validate(record, sources)
    controls = []
    replacements = [
        ("current-generic.rs", "InterpolateMatrix { .. } | AccumulateMatrix { .. } => return Err(()),", "InterpolateMatrix { .. } | AccumulateMatrix { .. } => Transform3D::identity(),"),
        ("current-generic.rs", "| AccumulateMatrix { .. }", ""),
        ("current-generic.rs", "operation.to_3d_matrix(reference_box)?", "operation.to_3d_matrix(reference_box).unwrap()"),
        ("current-generic.rs", "matrix.then(&transform)", "transform.then(&matrix)"),
        ("animated.rs", "components_to_transform_3d_matrix(left, None)?", "components_to_transform_3d_matrix(right, None)?"),
        ("animated.rs", "components_to_transform_3d_matrix(right, None)?", "components_to_transform_3d_matrix(left, None)?"),
        ("animated.rs", "Transform(left.to_vec().into())", "Transform(right.to_vec().into())"),
        ("animated.rs", "Transform(right.to_vec().into())", "Transform(left.to_vec().into())"),
    ]
    for index, (name, old, new) in enumerate(replacements):
        mutated = copy.deepcopy(sources)
        if old not in mutated[name]:
            raise ValueError("Missing source-control target")
        mutated[name] = mutated[name].replace(old, new, 1)
        try:
            validate(record, mutated)
        except ValueError as exc:
            controls.append({"index": index, "rejected": str(exc)})
        else:
            raise ValueError("Accepted source mutation")
    pins = [BASE / "SOURCE-v1.json", BASE / "SPEC-v1.json"] + [BASE / name for name in sources]
    for item in json.loads((BASE / "SPEC-v1.json").read_text()):
        path = BASE / item["excerpt"]
        if sha(path) != item["excerpt_sha256"]:
            raise ValueError("Spec excerpt hash")
        pins.append(path)
    if live:
        for key, snapshot in (("generic", "current-generic.rs"), ("animated", "animated.rs")):
            path = ROOT / record["paths"][key]
            if sha(path) != record["sha256"][snapshot]:
                raise ValueError("Live native hash: " + key)
            pins.append(path)
    return {"live_native_verified": live, "parent": record["parent"],
            "bridge": "Manual correspondence checked by exact snapshots and tokens; not Rust extraction",
            "snapshot_hashes": record["sha256"], "source_controls": controls}, pins
