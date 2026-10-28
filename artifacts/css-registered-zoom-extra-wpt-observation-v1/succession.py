def expected_policy(root, here, binding, helper):
    base = root / binding["base"]
    broad = root / binding["broad"]
    helper.authenticate(base, binding["base_manifest_sha256"])
    helper.authenticate(broad, binding["broad_manifest_sha256"])
    policy = helper.read(base / "POLICY.json")
    broad_policy = helper.read(broad / "POLICY.json")
    receipt = helper.read(broad / "HEAD-SUCCESSION.json")
    for key in ["application_ini", "forbidden_environment", "helpers", "manifest",
                "normal_binaries", "profile_directories", "runtime_inputs", "server_protocols",
                "unchanged_native_sources", "wpt_config", "frozen_head"]:
        policy[key] = broad_policy[key]
    policy.update(native_sources=broad_policy["source_roles"]["candidate"],
                  candidate_binaries=receipt["candidate_binaries"],
                  epoch_sha256=receipt["current_epoch_sha256"], source_role="zoom-normalization-v3",
                  build_result=receipt["build_result"],
                  build_result_sha256=receipt["pins"][receipt["build_result"]],
                  tests={}, target_subtests={}, live_oracle_sources={})
    expected = {"registered-animation-length-zoom.html":6,
                "registered-numeric-style-range-zoom.html":8}
    helper.need(len(binding["fixtures"]) == 2 and
                {f["html"]:f["count"] for f in binding["fixtures"]} == expected,
                "exact two fixture identities")
    for fixture in binding["fixtures"]:
        directory = root / fixture["directory"]
        helper.authenticate(directory, fixture["manifest_sha256"])
        names = helper.read(directory / fixture["check"])["test_names"]
        helper.need(len(names) == len(set(names)) == fixture["count"], "exact fixture names")
        url = "/css/css-properties-values-api/" + fixture["html"]
        policy["tests"][url] = "testharness"
        policy["target_subtests"][url] = names
        for name in ["testing/web-platform/tests" + url,
                     "testing/web-platform/meta" + url + ".ini"]:
            policy["live_oracle_sources"][name] = None
    return policy, broad, broad_policy


def validate(root, here, policy, helper):
    binding = helper.read(here / "BINDING.json")
    expected, broad, broad_policy = expected_policy(root, here, binding, helper)
    helper.need(policy == expected, "exact lifecycle/native/build/epoch/fixture policy")
    sources = helper.read(here / "SOURCE-PINS.json")
    original_sources = helper.read(root / binding["base"] / "SOURCE-PINS.json")
    shared = {name:item for name,item in original_sources.items()
              if "/css/css-properties-values-api/registered-" not in name}
    wanted = dict(shared)
    for fixture in binding["fixtures"]:
        url = "/css/css-properties-values-api/" + fixture["html"]
        origin = root / fixture["directory"] / fixture["html"]
        name = "testing/web-platform/tests" + url
        wanted[name] = {"bytes":origin.stat().st_size, "capture":"capture/" + name,
                        "exists":True, "origin":str(origin.relative_to(root)),
                        "sha256":helper.sha(origin)}
    helper.need(sources == wanted, "exact two captures and unchanged shared metadata/resources")
    for item in sources.values():
        if item["exists"]:
            helper.need(helper.sha(here / item["capture"]) == item["sha256"], "captured source body")
    helper.need(helper.read(here / "SELECTED.json") == policy["tests"] and
                helper.read(here / "TARGET-SUBTESTS.json") == policy["target_subtests"], "manifest selection identity")
    module = helper.load("sealed_broad_zoom_succession", broad / "succession.py")
    result = module.validate(root, broad, broad_policy, helper)
    preceding = helper.read(here / "PRECEDING-RUN.json")
    for name, pin in preceding["pins"].items():
        helper.need(helper.sha(root / name) == pin, "preceding saved broad run: " + name)
    directory = root / preceding["directory"]
    assessment = helper.read(directory / "ASSESSMENT.json")
    outcome = helper.read(directory / "RESULT.json")
    helper.need(assessment["complete"] and assessment["execution_preserved"] and
                outcome["observation_gate_passed"] and outcome["comparison_gate_passed"] and
                outcome["execution_error"] is None and outcome["preservation_error"] is None,
                "preceding broad run completed and preserved")
    helper.need(assessment["epoch_sha256"] == policy["epoch_sha256"] and
                assessment["native_sources"] == policy["native_sources"] and
                assessment["capsule_manifest_sha256"] == binding["broad_manifest_sha256"] and
                helper.sha(directory / "EPOCH.json") == policy["epoch_sha256"] and
                helper.read(directory / "NORMAL-BINARIES.json") == policy["candidate_binaries"],
                "preceding current source/binary/epoch provenance")
    metadata = helper.read(directory / "APPLICATION-METADATA.json")
    helper.need(metadata == helper.read(directory / "APPLICATION-METADATA-POST.json") == assessment["run_binding"] and
                metadata["revision"] == policy["frozen_head"] and
                helper.read(directory / "PRE.json") == helper.read(directory / "POST.json"),
                "preceding metadata and preservation")
    cleanup = helper.read(directory / "CLEANUP.json")
    helper.need(cleanup["owned_group_absent"] and cleanup["temporary_root_removed"], "preceding process cleanup")
    return dict(result, preceding_assessment_sha256=helper.sha(directory / "ASSESSMENT.json"),
                preceding_run_binding=metadata, observation_pages=2, observation_tests=14,
                observation_only=True, native_fix_acceptance=False)
