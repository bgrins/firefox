def bind(ROOT, epoch, settings, read, sha, authenticate, need):
    state, receipt = read(epoch / "STATE.json"), read(epoch / "ROOT-FINAL-CHECK.json")
    before, final = read(epoch / "BEFORE.json"), read(epoch / "FINAL.json")
    test = read(epoch / "TEST-INSTALLATION.json")
    owned = read(epoch / "OWNED-TEST.json")
    c = read(epoch / "CONFIG.json")
    acceptance = ROOT / settings["acceptance"]
    authenticate(read(acceptance.parent / "FILES.json"), acceptance.parent)
    need(sha(acceptance) == settings["acceptance_sha256"], "exact expanded acceptance")
    accepted = read(acceptance)
    need(accepted["status"] == "SCOPED_ACCEPTED" and accepted["fix"] == 114
         and accepted["native_changes_from_v1"] is False and accepted["landing_cases"] == 15
         and accepted["final_path_validation"]["directory"] == str(epoch.relative_to(ROOT))
         and accepted["final_path_validation"]["files_sha256"] == sha(epoch / "FILES.json"), "expanded acceptance epoch join")
    need(sha(ROOT / accepted["patch"]["path"]) == accepted["patch"]["sha256"], "accepted expanded patch")
    need(state["status"] == "terminal" and state["complete"] is True
         and state["expanded_test_installed"] is True and state["native_changes"] is False
         and state["lint_exit"] == 0 and state["counts"] == {"PASS":15,"FAIL":0}
         and state["files_ok"] == 2 and "failure" not in state, "successful expanded test installation")
    need(receipt["status"] == "TEST_SCOPE_INSTALLED_VERIFIED" and receipt["exit"] == 0
         and receipt["state_sha256"] == sha(epoch / "STATE.json")
         and receipt["final_sha256"] == sha(epoch / "FINAL.json")
         and receipt["native_sources_index_binaries_unchanged"] is True
         and receipt["prior4_test_identities_preserved"] is True
         and receipt["new_font_test_identity_verified"] is True, "root preservation receipt")
    need(test["before"] == before and test["after"] == final and test["owned_test"] == owned
         and test["native_changes"] is False and before["snapshot"] == final["snapshot"]
         and final["pins"] == {**before["pins"], owned["path"]:owned["sha256"]}, "only test scope changed")
    expected, pins = final["snapshot"], dict(final["pins"])
    need(len(expected["sources"]) == receipt["source_count"] == len(c["guard_sources"]) == 52
         and len(pins) == receipt["pin_count"] == 372 and receipt["staged_paths_preserved"] == 925
         and receipt["native_modified_paths"] == 29, "exact final roles")
    installed_tests = {**c["installed_tests"], owned["path"]:{"identity":owned["identity"],"sha256":owned["sha256"]}}
    need(len(c["installed_tests"]) == 4 and owned["path"] not in c["installed_tests"]
         and installed_tests == receipt["installed_tests"] and len(installed_tests) == 5
         and all(pins[n] == item["sha256"] for n,item in installed_tests.items()), "five installed identities")
    prior = ROOT / accepted["installation"]["directory"]
    need(sha(prior / "FILES.json") == accepted["installation"]["files_sha256"], "native installation seal")
    authenticate(read(prior / "FILES.json"), prior)
    installation = read(prior / "INSTALLATION.json")
    original_config = read(prior / "CONFIG.json")
    old_tests = {**original_config["installed_tests"], installation["owned_test"]:{"identity":installation["owned_test_identity"],"sha256":installation["owned_test_sha256"]}}
    need(old_tests == c["installed_tests"] and installation["after"] == expected, "native installation/source/old ownership join")
    need(all(pins[n] == h for n,h in installation["binary_pins"].items())
         and receipt["installed_binary_pins"] == installation["binary_pins"], "actual installed binaries")
    repair = ROOT / settings["repair_proposal"]
    authenticate(read(repair / "FILES.json"), repair)
    source_map = read(repair / "SOURCE-PINS.json")
    need(set(source_map) == {"dom/svg/DOMSVGLength.cpp","dom/svg/DOMSVGLength.h"}
         and installation["installed_source_pins"] == {n:v["candidate_sha256"] for n,v in source_map.items()}
         and installation["original_source_pins"] == {n:v["before_sha256"] for n,v in source_map.items()}, "exact accepted native bodies")
    for name,digest in read(ROOT / settings["proposal"] / "SOURCE-PINS.json")["files"].items():
        if name in source_map:
            need(digest == source_map[name]["before_sha256"], "audit original source")
            digest = source_map[name]["candidate_sha256"]
        need(name not in pins or pins[name] == digest, "audit input conflicts with installed roles")
        pins[name] = digest
    c["modified_native_paths"] = sorted(set(original_config["modified_native_paths"]) | set(source_map))
    need(len(c["modified_native_paths"]) == 29, "exact native roster")
    c["must_be_absent"] = original_config["must_be_absent"]
    c["existing_tests"] = sorted(installed_tests)
    c["existing_test_pins"] = {n:v["sha256"] for n,v in installed_tests.items()}
    c["tracked_existing_tests"] = []
    return state, receipt, expected, pins, c, installed_tests
