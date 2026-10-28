def validate(root, here, policy, helper):
    binding = helper.read(here / "BINDING.json")
    base = root / binding["base"]
    helper.authenticate(base, binding["base_manifest_sha256"])
    original = helper.read(base / "POLICY.json")
    changed = {"tests", "target_subtests", "live_oracle_sources"}
    helper.need(set(policy) == set(original), "same policy schema")
    helper.need({k:v for k,v in policy.items() if k not in changed} ==
                {k:v for k,v in original.items() if k not in changed}, "unchanged native/build/epoch/lifecycle policy")
    fixture = root / binding["fixture"]
    helper.authenticate(fixture, binding["fixture_manifest_sha256"])
    names = helper.read(fixture / "STATIC-CHECK.json")["test_names"]
    url = "/css/css-properties-values-api/registered-logical-unit-writing-mode.html"
    helper.need(policy["tests"] == {url:"testharness"} and policy["target_subtests"] == {url:names} and len(names) == 16, "exact new fixture identities")
    helper.need(policy["live_oracle_sources"] == {"testing/web-platform/tests" + url:None,
                "testing/web-platform/meta" + url + ".ini":None}, "canonical fixture remains absent")
    module = helper.load("sealed_zoom_calibration_succession", base / "succession.py")
    result = module.validate(root, base, original, helper)
    return dict(result, calibration_fixture=str(fixture), calibration_fixture_sha256=binding["fixture_manifest_sha256"])
