import base64
import hashlib
import importlib.util
import json
from pathlib import Path
import re
from urllib.parse import urlsplit

spec = importlib.util.spec_from_file_location("page_png", Path(__file__).with_name("pixels.py"))
pixels = importlib.util.module_from_spec(spec)
spec.loader.exec_module(pixels)


def need(value, message):
    if not value:
        raise ValueError(message)


def signature(row):
    return {key: {"present": key in row, "value": row.get(key)}
            for key in ("status", "expected", "known_intermittent")}


def message_signature(message, allowed):
    found = re.findall(r"https?://[^\s]+", message)
    need(bool(found), "missing reference diagnostic URLs")
    ports = set()
    for value in found:
        url = urlsplit(value)
        need(url.scheme == "http" and url.hostname == "web-platform.test" and
             url.path in allowed and not url.query and not url.fragment and
             url.port is not None and 0 < url.port < 65536, "unexpected reference diagnostic URL")
        ports.add(url.port)
    need(len(ports) == 1, "mixed reference diagnostic ports")
    return re.sub(r"http://web-platform\.test:[0-9]+", "http://web-platform.test:PORT", message)


def assess(events, code, policy, checks, original=None, run_binding=None):
    errors, starts, ends = [], [], []
    suites, finishes, running, rows = [], 0, set(), []
    expected = set(policy["tests"])
    decoded = {}
    try:
        need(code in (0, 1), "unexpected WPT process exit")
        for event in events:
            action = event.get("action")
            if action == "suite_start":
                need(not suites and not starts and finishes == 0, "duplicate/late suite start")
                suites.append(event)
                selected = [name for names in event["tests"].values() for name in names]
                need(len(selected) == len(expected) and set(selected) == expected, "suite roster")
            elif action == "suite_end":
                need(len(suites) == 1 and not running and set(ends) == expected and finishes == 0, "early/duplicate suite end")
                finishes += 1
            elif action == "test_start":
                name = event["test"]
                need(len(suites) == 1 and finishes == 0 and name in expected and name not in starts, "test start identity/order")
                starts.append(name)
                running.add(name)
            elif action == "test_end":
                name = event["test"]
                need(name in running and name not in ends and event["status"] in ("PASS", "FAIL"), "test end identity/status")
                running.remove(name)
                ends.append(name)
                allowed = {name, *policy["references"][name]}
                shot_values = event.get("extra", {}).get("reftest_screenshots", [])
                need(len(shot_values) >= 3 and len(shot_values) % 3 == 0, "missing/incomplete print comparison screenshots")
                shots = []
                for index in range(0, len(shot_values), 3):
                    left, operator, right = shot_values[index:index + 3]
                    need(operator == "==", "unexpected print reference operator")
                    pair = []
                    for item, paths in ((left, {name}), (right, set(policy["references"][name]))):
                        need(isinstance(item, dict), "missing screenshot object")
                        url = urlsplit(item["url"])
                        need(url.hostname == "web-platform.test" and url.scheme == "http" and url.path in paths and not url.query and not url.fragment, "screenshot reference path")
                        data = base64.b64decode(item["screenshot"], validate=True)
                        digest = hashlib.sha256(data).hexdigest()
                        if digest not in decoded:
                            inspected = pixels.inspect(data)
                            width, height, scanlines = pixels.decode_png(data)
                            inspected["decoded_sha256"] = hashlib.sha256(b"".join(scanlines)).hexdigest()
                            decoded[digest] = inspected
                        image = decoded[digest]
                        if name in policy["target_pages"]:
                            need(image["green_pixels"] == 400 and image["other_nonwhite_colors"] == [], "target screenshot vacuity/geometry")
                        pair.append({"path": url.path, **image})
                    if event["status"] == "PASS":
                        need((pair[0]["width"], pair[0]["height"]) == (pair[1]["width"], pair[1]["height"]), "PASS image dimensions disagree")
                        if pair[0]["decoded_sha256"] != pair[1]["decoded_sha256"]:
                            tolerance = policy["fuzzy"].get(name)
                            need(tolerance is not None, "PASS pixels disagree without captured fuzzy metadata")
                            left_rows = pixels.decode_png(base64.b64decode(left["screenshot"], validate=True))[2]
                            right_rows = pixels.decode_png(base64.b64decode(right["screenshot"], validate=True))[2]
                            differences = [max(abs(a - b) for a, b in zip(x[i:i+4], y[i:i+4]))
                                           for x, y in zip(left_rows, right_rows) for i in range(0, len(x), 4)]
                            need(max(differences) <= tolerance["max_difference"] and
                                 sum(d > 0 for d in differences) <= tolerance["total_pixels"], "PASS exceeds captured fuzzy metadata")
                    shots.append(pair)
                rows.append({"test": name, "signature": signature(event),
                             "message": event.get("message", ""),
                             "message_without_port": message_signature(event.get("message", ""), allowed),
                             "screenshots": shots})
            elif action in ("test_status", "crash", "process_crash"):
                raise ValueError("unexpected event: " + action)
            elif action == "log" and event.get("level") in ("ERROR", "CRITICAL"):
                raise ValueError("harness error: " + event.get("message", ""))
        need(len(suites) == finishes == 1 and len(starts) == len(ends) == len(expected) and not running, "incomplete run")
        info = suites[0]["run_info"]
        need(info["revision"] == run_binding["revision"] and info["browser_build_id"] == run_binding["browser_build_id"], "unbound revision/BuildID")
        need(code == (1 if any(r["signature"]["status"]["value"] == "FAIL" for r in rows) else 0), "WPT exit/status disagreement")
    except (ValueError, KeyError, TypeError, AssertionError) as exc:
        errors.append(str(exc))
    return {"complete": not errors, "errors": errors, "starts": starts, "ends": ends,
            "rows": rows, "run_info": suites[0].get("run_info") if suites else None,
            "run_binding": run_binding, "wpt_exit": code}


def compare(candidate, original, policy):
    if original is None:
        return {"complete": candidate["complete"], "paired": False, "repairs": [], "errors": []}
    errors, repairs = [], []
    try:
        need(candidate["complete"] and original["complete"] and original["execution_preserved"], "incomplete paired evidence")
        a, b = dict(original["run_info"]), dict(candidate["run_info"])
        for info, assessment in ((a, original), (b, candidate)):
            need(info["browser_build_id"] == assessment["run_binding"]["browser_build_id"], "unbound phase BuildID")
            info.pop("browser_build_id")
        need(a == b, "non-BuildID run_info drift")
        old = {r["test"]: r for r in original["rows"]}
        new = {r["test"]: r for r in candidate["rows"]}
        need(set(old) == set(new) == set(policy["tests"]), "paired identities")
        for name in sorted(new):
            left, right = old[name], new[name]
            need(right["signature"]["status"]["value"] == "PASS", "candidate failure: " + name)
            need(left["signature"]["known_intermittent"] == right["signature"]["known_intermittent"], "intermittent metadata drift: " + name)
            refs = lambda row: [(pair[1]["path"], pair[1]["decoded_sha256"], pair[1]["width"], pair[1]["height"]) for pair in row["screenshots"]]
            need(refs(left) == refs(right), "reference pixels/order changed: " + name)
            if left["signature"]["status"]["value"] == "FAIL":
                need(name in policy["target_pages"], "existing regression baseline failed: " + name)
                repairs.append(name)
            else:
                need(left["signature"] == right["signature"] and left["message_without_port"] == right["message_without_port"], "unchanged control signature changed: " + name)
        need(bool(repairs), "no observed original failures repaired")
    except (ValueError, KeyError, TypeError) as exc:
        errors.append(str(exc))
    return {"complete": not errors, "paired": True, "repairs": repairs, "errors": errors,
            "port_normalization": "Only validated localhost WPT diagnostic URL ports; raw messages retained"}
