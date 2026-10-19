#!/usr/bin/env python3
import argparse
import hashlib
import json
from pathlib import Path
import socket
import subprocess
import tempfile
import time

ROOT = Path(__file__).resolve().parent


class Marionette:
    def __init__(self, connection):
        self.connection = connection
        self.connection.settimeout(30)
        self.stream = connection.makefile("rb")
        self.sequence = 0
        self.hello = self.receive()
        if self.hello.get("marionetteProtocol") != 3:
            raise RuntimeError(f"Unsupported Marionette handshake: {self.hello}")

    def receive(self):
        length = bytearray()
        while True:
            byte = self.stream.read(1)
            if byte == b":":
                break
            if not byte or not byte.isdigit() or len(length) > 12:
                raise RuntimeError("Invalid Marionette frame")
            length.extend(byte)
        size = int(length)
        payload = self.stream.read(size)
        if len(payload) != size:
            raise RuntimeError("Truncated Marionette frame")
        return json.loads(payload)

    def request(self, method, parameters):
        self.sequence += 1
        payload = json.dumps([0, self.sequence, method, parameters]).encode()
        self.connection.sendall(str(len(payload)).encode() + b":" + payload)
        result = self.receive()
        if result[:2] != [1, self.sequence]:
            raise RuntimeError(f"Unexpected Marionette response: {result}")
        if result[2] is not None:
            raise RuntimeError(f"Marionette error: {result[2]}")
        return result[3]

    def close(self):
        self.stream.close()
        self.connection.close()


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--firefox", required=True)
    parser.add_argument("--lake", default="lake")
    parser.add_argument("--fixture-suite", choices=("selectors", "content", "computed", "variables", "guarded", "keywords", "custom", "layers", "layer-custom", "parsed-values", "scope", "ordered-queries", "parsed-selectors", "parsed-style", "parsed-attributes", "parsed-structural", "anb", "parsed-indexed", "parsed-of", "parsed-negation", "parsed-recursive", "parsed-logical", "parsed-has", "component-selectors", "component-attributes", "component-attribute-discrepancies", "component-anb", "component-indexed", "recursive-component", "logical-component", "has-component", "component-style", "forgiving-component", "forgiving-has", "forgiving-has-style", "certified-component", "certified-recovery", "certified-recovery-style", "forbidden-recovery", "forbidden-recovery-style", "type-head-html", "type-head-xml", "host-compound-html", "host-compound-xml", "identity-html-standard", "identity-html-quirks", "identity-xml", "host-chain-html-standard", "host-chain-html-quirks", "host-chain-xml", "host-logical-html-standard", "host-logical-html-quirks", "host-logical-xml", "scope-cascade", "numeric-opacity", "host-visibility", "host-structural-html-standard", "host-structural-html-quirks", "host-structural-xml", "structural-visibility", "host-forgiving-html-standard", "host-forgiving-html-quirks", "host-forgiving-xml", "forgiving-visibility", "host-relational-html-standard", "host-relational-html-quirks", "host-relational-xml", "relational-visibility", "layer-visibility", "nested-layer-visibility", "anonymous-layer-visibility", "conditional-layer-visibility"), default="selectors")
    args = parser.parse_args()
    evidence = ROOT / ".lake" / "browser-check"
    if args.fixture_suite != "selectors":
        evidence /= args.fixture_suite
    evidence.mkdir(parents=True, exist_ok=True)
    report_path = evidence / "report.json"
    report_path.unlink(missing_ok=True)
    proof_path = ROOT / ".lake" / "verification" / "report.json"
    proof_bytes = proof_path.read_bytes()
    proof = json.loads(proof_bytes)
    if proof["status"] != "pass":
        raise RuntimeError("Run check.py successfully before browser verification")
    source_hashes = proof["source_sha256"]
    required = {str(path.relative_to(ROOT)) for path in (ROOT / "CssSemantics").rglob("*.lean")}
    exporter = {"selectors": "tests/ExportBrowserFixtures.lean",
                "content": "tests/ExportContentFixtures.lean",
                "computed": "tests/ExportComputedFixtures.lean",
                "variables": "tests/ExportVariablesFixtures.lean",
                "guarded": "tests/ExportGuardedFixtures.lean",
                "keywords": "tests/ExportKeywordFixtures.lean",
                "custom": "tests/ExportCustomFixtures.lean",
                "layers": "tests/ExportLayerFixtures.lean",
                "layer-custom": "tests/ExportLayerCustomFixtures.lean",
                "parsed-values": "tests/ExportParsedFixtures.lean",
                "scope": "tests/ExportScopeFixtures.lean",
                "ordered-queries": "tests/ExportOrderedFixtures.lean",
                "parsed-selectors": "tests/ExportParsedSelectorFixtures.lean",
                "parsed-style": "tests/ExportParsedStyleFixtures.lean",
                "parsed-attributes": "tests/ExportAttributeFixtures.lean",
                "parsed-structural": "tests/ExportStructuralFixtures.lean",
                "anb": "tests/ExportAnBFixtures.lean",
                "parsed-indexed": "tests/ExportIndexedFixtures.lean",
                "parsed-of": "tests/ExportOfFixtures.lean",
                "parsed-negation": "tests/ExportNegationFixtures.lean",
                "parsed-recursive": "tests/ExportRecursiveSelectorFixtures.lean",
                "parsed-logical": "tests/ExportLogicalSelectorFixtures.lean",
                "parsed-has": "tests/ExportHasSelectorFixtures.lean",
                "component-selectors": "tests/ExportComponentSelectorFixtures.lean",
                "component-attributes": "tests/ExportComponentAttributeFixtures.lean",
                "component-attribute-discrepancies": "tests/ExportComponentAttributeDiscrepancies.lean",
                "component-anb": "tests/ExportComponentAnBFixtures.lean",
                "component-indexed": "tests/ExportComponentIndexedFixtures.lean",
                "recursive-component": "tests/ExportRecursiveComponentFixtures.lean",
                "logical-component": "tests/ExportLogicalComponentFixtures.lean",
                "has-component": "tests/ExportHasComponentFixtures.lean",
                "component-style": "tests/ExportComponentStyleFixtures.lean",
                "forgiving-component": "tests/ExportForgivingComponentFixtures.lean",
                "forgiving-has": "tests/ExportForgivingHasFixtures.lean",
                "forgiving-has-style": "tests/ExportForgivingHasStyleFixtures.lean",
                "certified-component": "tests/ExportCertifiedComponentFixtures.lean",
                "certified-recovery": "tests/ExportCertifiedRecoveryFixtures.lean",
                "certified-recovery-style": "tests/ExportCertifiedRecoveryStyleFixtures.lean",
                "forbidden-recovery": "tests/ExportForbiddenRecoveryFixtures.lean",
                "forbidden-recovery-style": "tests/ExportForbiddenRecoveryStyleFixtures.lean",
                "scope-cascade": "tests/ExportScopedCascadeFixtures.lean",
                "numeric-opacity": "tests/ExportOpacityFixtures.lean",
                "host-visibility": "tests/ExportHostVisibilityFixtures.lean",
                "relational-visibility": "tests/ExportRelationalVisibilityFixtures.lean",
                "layer-visibility": "tests/ExportLayerVisibilityFixtures.lean",
                "nested-layer-visibility": "tests/ExportNestedLayerVisibilityFixtures.lean",
                "anonymous-layer-visibility": "tests/ExportAnonymousLayerVisibilityFixtures.lean",
                "conditional-layer-visibility": "tests/ExportConditionalLayerVisibilityFixtures.lean",
                "host-relational-html-standard": "tests/ExportHostRelationalFixtures.lean",
                "host-relational-html-quirks": "tests/ExportHostRelationalFixtures.lean",
                "host-relational-xml": "tests/ExportHostRelationalFixtures.lean",
                "forgiving-visibility": "tests/ExportForgivingVisibilityFixtures.lean",
                "host-forgiving-html-standard": "tests/ExportHostForgivingFixtures.lean",
                "host-forgiving-html-quirks": "tests/ExportHostForgivingFixtures.lean",
                "host-forgiving-xml": "tests/ExportHostForgivingFixtures.lean",
                "structural-visibility": "tests/ExportStructuralVisibilityFixtures.lean",
                "host-structural-html-standard": "tests/ExportHostStructuralFixtures.lean",
                "host-structural-html-quirks": "tests/ExportHostStructuralFixtures.lean",
                "host-structural-xml": "tests/ExportHostStructuralFixtures.lean",
                "type-head-html": "tests/ExportExplicitTypeHeadFixtures.lean",
                "type-head-xml": "tests/ExportExplicitTypeHeadFixtures.lean",
                "host-compound-html": "tests/ExportHostCompoundFixtures.lean",
                "host-compound-xml": "tests/ExportHostCompoundFixtures.lean",
                "identity-html-standard": "tests/ExportHostIdentityFixtures.lean",
                "identity-html-quirks": "tests/ExportHostIdentityFixtures.lean",
                "identity-xml": "tests/ExportHostIdentityFixtures.lean",
                "host-chain-html-standard": "tests/ExportHostSelectorChainFixtures.lean",
                "host-chain-html-quirks": "tests/ExportHostSelectorChainFixtures.lean",
                "host-chain-xml": "tests/ExportHostSelectorChainFixtures.lean",
                "host-logical-html-standard": "tests/ExportHostLogicalFixtures.lean",
                "host-logical-html-quirks": "tests/ExportHostLogicalFixtures.lean",
                "host-logical-xml": "tests/ExportHostLogicalFixtures.lean"}[args.fixture_suite]
    required.update({"CssSemantics.lean", exporter, "lean-toolchain",
                     "lakefile.lean", "lake-manifest.json", "browser_check.py",
                     "browser/runner.js", "browser/computed.js", "browser/index.html"})
    if not required.issubset(source_hashes):
        raise RuntimeError("Proof report does not cover all browser dependencies")

    def verify_sources():
        for name, digest in source_hashes.items():
            if hashlib.sha256((ROOT / name).read_bytes()).hexdigest() != digest:
                raise RuntimeError(f"Source differs from checked proof report: {name}")

    verify_sources()
    export_command = [args.lake, "env", "lean", "--run", exporter]
    if args.fixture_suite in ("type-head-html", "type-head-xml", "host-compound-html", "host-compound-xml"):
        export_command.append("html" if args.fixture_suite.endswith("-html") else "xml")
    if args.fixture_suite.startswith("host-chain-"):
        export_command.append(args.fixture_suite.removeprefix("host-chain-"))
    if args.fixture_suite.startswith("host-logical-"):
        export_command.append(args.fixture_suite.removeprefix("host-logical-"))
    if args.fixture_suite.startswith("host-relational-"):
        export_command.append(args.fixture_suite.removeprefix("host-relational-"))
    if args.fixture_suite.startswith("host-forgiving-"):
        export_command.append(args.fixture_suite.removeprefix("host-forgiving-"))
    if args.fixture_suite.startswith("host-structural-"):
        export_command.append(args.fixture_suite.removeprefix("host-structural-"))
    if args.fixture_suite.startswith("identity-"):
        export_command.append(args.fixture_suite.removeprefix("identity-"))
    exported = subprocess.run(export_command, cwd=ROOT, capture_output=True, text=True, check=True)
    fixtures = json.loads(exported.stdout)
    if exported.stderr or not fixtures["cases"]:
        raise RuntimeError(f"Unexpected fixture export: {exported.stderr}")
    names = [case["name"] for case in fixtures["cases"]]
    if len(set(names)) != len(names):
        raise RuntimeError("Duplicate browser case names")
    verify_sources()
    (evidence / "fixtures.json").write_text(exported.stdout)
    with socket.socket() as reservation:
        reservation.bind(("127.0.0.1", 0))
        port = reservation.getsockname()[1]
    profile = Path(tempfile.mkdtemp(prefix="profile-", dir=evidence))
    preferences = {
        "marionette.port": port,
        "browser.shell.checkDefaultBrowser": False,
        "browser.startup.page": 0,
        "browser.startup.homepage": "about:blank",
        "browser.startup.homepage_override.mstone": "ignore",
        "browser.sessionstore.resume_from_crash": False,
    }
    (profile / "user.js").write_text("\n".join(
        f"user_pref({json.dumps(key)}, {json.dumps(value)});" for key, value in preferences.items()) + "\n")
    command = [str(Path(args.firefox).resolve()), "--headless", "--marionette", "--no-remote",
               "--profile", str(profile)]
    client = None
    with (evidence / "firefox.log").open("w") as log:
        process = subprocess.Popen(command, stdout=log, stderr=subprocess.STDOUT)
        try:
            deadline = time.monotonic() + 45
            while True:
                if process.poll() is not None:
                    raise RuntimeError(f"Firefox exited {process.returncode}; see {evidence / 'firefox.log'}")
                try:
                    connection = socket.create_connection(("127.0.0.1", port), timeout=1)
                    break
                except OSError:
                    if time.monotonic() >= deadline:
                        raise RuntimeError("Timed out waiting for isolated Firefox")
                    time.sleep(0.1)
            client = Marionette(connection)
            session = client.request("WebDriver:NewSession", {"capabilities": {"alwaysMatch": {}}})
            client.request("WebDriver:Navigate", {"url": (ROOT / "browser" / "index.html").as_uri()})
            result = client.request("WebDriver:ExecuteAsyncScript", {
                "script": """
                  const done = arguments[arguments.length - 1];
                  const data = arguments[0];
                  const run = data.schemaVersion === 3 ? window.wrappedJSObject.runCssComputedFixtures :
                    window.wrappedJSObject.runCssFixtures;
                  Promise.resolve().then(() => run(data)).then(done,
                    error => done({harnessError: String(error)}));
                """,
                "args": [fixtures], "newSandbox": True, "sandbox": "default",
                "line": 1, "filename": "browser_check.py",
            })
            browser = result.get("value", result)
            if "harnessError" in browser:
                raise RuntimeError(browser["harnessError"])
            if browser["schemaVersion"] != fixtures["schemaVersion"] or browser["profile"] != fixtures["profile"]:
                raise RuntimeError("Browser fixture schema or profile changed")
            if fixtures.get("htmlStandardMode") is True and browser.get("htmlStandardModeVerified") is not True:
                raise RuntimeError("HTML standards-mode profile was not checked")
            if "documentLanguage" in fixtures:
                language = fixtures["documentLanguage"]
                observed = browser.get("documentObservation")
                if (language not in ("html", "xml") or browser.get("documentLanguageVerified") is not True or
                        type(observed) is not dict or observed.get("language") != language or
                        observed.get("contentType") != ("text/html" if language == "html" else "application/xml") or
                        observed.get("compatMode") != ("BackCompat" if fixtures.get("documentMode") == "quirks" else "CSS1Compat")):
                    raise RuntimeError("Document-language profile was not checked")
            if "documentMode" in fixtures:
                mode = fixtures["documentMode"]
                observed_mode = browser.get("documentModeObservation")
                construction = ("create-xml-document" if fixtures["documentLanguage"] == "xml" else
                                "parse-html-without-doctype" if mode == "quirks" else "create-html-document")
                if (mode not in ("no-quirks", "quirks") or browser.get("documentModeVerified") is not True or
                        type(observed_mode) is not dict or observed_mode != {
                            "mode": mode, "construction": construction,
                            "compatMode": "BackCompat" if mode == "quirks" else "CSS1Compat"}):
                    raise RuntimeError("Document mode was not checked")
            results = browser["results"]
            if browser["snapshotVerified"] is not True or len(results) != len(fixtures["cases"]):
                raise RuntimeError("Browser snapshot or case count changed")
            passed = 0
            for expected, actual in zip(fixtures["cases"], results):
                keys = ("name", "css", "node", "expected", "scenario") if fixtures["schemaVersion"] == 3 else ("name", "css", "node", "expected")
                if fixtures["schemaVersion"] == 4:
                    keys += ("api", "candidate")
                if fixtures["schemaVersion"] == 5:
                    keys += ("api",)
                if fixtures["schemaVersion"] == 6:
                    keys += ("expectedError",)
                if any(actual[key] != expected[key] for key in keys):
                    raise RuntimeError("Browser result case changed")
                result_type = str if fixtures["schemaVersion"] == 3 else bool
                expects_syntax_error = fixtures["schemaVersion"] == 6 and expected["expectedError"] == "SyntaxError"
                if fixtures["schemaVersion"] == 6:
                    if expected["expectedError"] not in (None, "SyntaxError"):
                        raise RuntimeError("Invalid syntax error expectation")
                    if actual["error"] is None:
                        if actual["errorName"] is not None:
                            raise RuntimeError("Inconsistent exception name")
                    elif not (type(actual["error"]) is str and type(actual["errorName"]) is str and actual["actual"] is None):
                        raise RuntimeError("Invalid syntax exception observation")
                    if expects_syntax_error:
                        result_type = type(None)
                if fixtures["schemaVersion"] == 5 and expected["api"] == "query-all":
                    result_type = list
                    if any(type(key) is not str for key in expected["expected"]):
                        raise RuntimeError("Invalid ordered query expectation")
                if (fixtures["schemaVersion"] == 4 and expected["api"] == "closest" or
                        fixtures["schemaVersion"] == 5 and expected["api"] == "query-first"):
                    result_type = type(expected["expected"])
                    if result_type not in (str, type(None)):
                        raise RuntimeError("Invalid closest expectation")
                if type(expected["expected"]) is not result_type:
                    raise RuntimeError("Invalid expected result type")
                success = (actual["error"] is None and type(actual["actual"]) is result_type
                           and actual["actual"] == expected["expected"])
                if expects_syntax_error:
                    success = actual["errorName"] == "SyntaxError" and actual["actual"] is None
                if actual["pass"] is not success:
                    raise RuntimeError("Inconsistent browser result")
                passed += success
            if browser["total"] != len(results) or browser["passed"] != passed:
                raise RuntimeError("Inconsistent browser counters")
            if fixtures["schemaVersion"] == 3:
                if fixtures["property"] not in ("visibility", "opacity") or browser["property"] != fixtures["property"]:
                    raise RuntimeError("Computed property changed")
                if browser.get("opacityAdmissionVerified") is not (fixtures.get("opacityAdmission") is True):
                    raise RuntimeError("Opacity admission profile changed")
                if fixtures.get("opacityAdmission") is True and any(sheet.get("declarationAccepted") is not True for sheet in browser["sheets"]):
                    raise RuntimeError("Opacity declaration admission was not verified")
                if [(sheet["name"], sheet["css"]) for sheet in browser["sheets"]] != [
                    (scenario["name"], scenario["css"]) for scenario in fixtures["scenarios"]]:
                    raise RuntimeError("Computed stylesheet observations changed")
                if any(type(sheet["parsedRules"]) is not int or sheet["parsedRules"] < 0 for sheet in browser["sheets"]):
                    raise RuntimeError("Invalid stylesheet observation")
                if browser.get("stylesheetAdmissionVerified") is not (fixtures.get("stylesheetAdmission") is True):
                    raise RuntimeError("Visibility stylesheet admission profile changed")
                if browser.get("layerAdmissionVerified") is not (fixtures.get("layerAdmission") is True):
                    raise RuntimeError("Layer stylesheet admission profile changed")
                if browser.get("conditionAdmissionVerified") is not (fixtures.get("conditionAdmission") is True):
                    raise RuntimeError("Global condition admission profile changed")
                if fixtures.get("conditionAdmission") is True and any(
                        sheet.get("mediumObservation") != {"screen": True, "print": False} for sheet in browser["sheets"]):
                    raise RuntimeError("Global condition medium was not observed")
                if fixtures.get("stylesheetAdmission") is True:
                    def agrees(actual, expected):
                        if type(actual) is not list or type(expected) is not list or len(actual) != len(expected):
                            return False
                        for rule, wanted in zip(actual, expected):
                            if type(rule) is not dict or type(wanted) is not dict or rule.get("kind") != wanted.get("kind"):
                                return False
                            if rule["kind"] == "layerStatement":
                                if rule.get("names") != wanted.get("names"):
                                    return False
                            elif rule["kind"] == "layerBlock":
                                if rule.get("name") != wanted.get("name") or not agrees(rule.get("children"), wanted.get("children")):
                                    return False
                            elif rule["kind"] in ("media", "supports"):
                                if (fixtures.get("conditionAdmission") is not True or
                                        rule.get("conditionText") != wanted.get("conditionText") or
                                        type(rule.get("conditionMatches")) is not bool or
                                        rule["conditionMatches"] is not wanted.get("conditionMatches") or
                                        not agrees(rule.get("children"), wanted.get("children"))):
                                    return False
                            elif rule["kind"] == "style":
                                if (type(rule.get("selectorText")) is not str or not rule["selectorText"] or
                                        rule.get("declarations") != wanted.get("declarations")):
                                    return False
                            else:
                                return False
                        return True
                    for scenario, sheet in zip(fixtures["scenarios"], browser["sheets"]):
                        if (sheet.get("documentObservation") != fixtures["computedDocument"] or
                                type(sheet.get("effectiveRules")) is not list or
                                len(sheet["effectiveRules"]) != sheet["parsedRules"]):
                            raise RuntimeError("Visibility stylesheet admission was not verified")
                        if fixtures.get("layerAdmission") is True:
                            admitted = agrees(sheet["effectiveRules"], scenario["effectiveRules"])
                        else:
                            admitted = (all(type(rule.get("selectorText")) is str and rule["selectorText"] for rule in sheet["effectiveRules"]) and
                                [rule.get("declarations") for rule in sheet["effectiveRules"]] == scenario["effectiveDeclarations"])
                        if not admitted:
                            raise RuntimeError("Visibility stylesheet admission was not verified")

            observations = browser.get("observations", [])
            expected_observations = fixtures.get("observations", [])
            if len(observations) != len(expected_observations):
                raise RuntimeError("Browser observation count changed")
            if browser.get("observationProfile") != fixtures.get("observationProfile"):
                raise RuntimeError("Browser observation profile changed")
            for expected, actual in zip(expected_observations, observations):
                keys = ("name", "css", "node", "expected")
                if fixtures["schemaVersion"] == 5:
                    keys += ("api",)
                if any(actual[key] != expected[key] for key in keys):
                    raise RuntimeError("Browser observation pair changed")
                if fixtures["schemaVersion"] == 5:
                    expected_type = list if expected["api"] == "query-all" else type(expected["expected"])
                    if actual["error"] is None:
                        if type(actual["actual"]) is not expected_type:
                            raise RuntimeError("Invalid ordered profile observation")
                    elif not (type(actual["error"]) is str and actual["actual"] is None):
                        raise RuntimeError("Invalid ordered profile error observation")
                    success = actual["error"] is None and actual["actual"] == expected["expected"]
                else:
                    if actual["error"] is not None or type(actual["actual"]) is not bool:
                        raise RuntimeError("Invalid browser profile observation")
                    success = actual["actual"] is expected["expected"]
                if actual["pass"] is not success:
                    raise RuntimeError("Inconsistent browser profile observation")
            control_result = client.request("WebDriver:ExecuteAsyncScript", {
                "script": """
                  const done = arguments[arguments.length - 1];
                  const data = arguments[0];
                  const baseline = arguments[1];
                  const run = data.schemaVersion === 3 ? window.wrappedJSObject.runCssComputedFixtures :
                    window.wrappedJSObject.runCssFixtures;
                  (async () => {
                  const snapshot = structuredClone(data);
                  snapshot.nodes[0].id = "deliberately-inconsistent-id";
                  let snapshotRejected = false;
                  try { await run(snapshot); } catch (error) {
                    snapshotRejected = String(error).includes("DOM snapshot mismatch:");
                  }
                  const controls = {snapshotRejected, mismatchDetected: false};
                  const flippedIndex = baseline.findIndex(result => result.pass === true && result.expectedError !== "SyntaxError");
                  if (flippedIndex >= 0) {
                    const flipped = structuredClone(data);
                    const previous = flipped.cases[flippedIndex].expected;
                    flipped.cases[flippedIndex].expected = Array.isArray(previous) ?
                      (previous.length > 1 ? previous.toReversed() : previous.length ? [] : [data.nodes[0].key]) :
                      (data.schemaVersion === 4 && flipped.cases[flippedIndex].api === "closest" ||
                       data.schemaVersion === 5 && flipped.cases[flippedIndex].api === "query-first") ?
                      (previous === null ? data.nodes[0].key : null) : data.schemaVersion === 3 ?
                      (data.property === "opacity" ? (previous === "0" ? "1" : "0") :
                        (previous === "visible" ? "hidden" : "visible")) :
                      !flipped.cases[flippedIndex].expected;
                    const mismatch = await run(flipped);
                    controls.mismatchDetected = mismatch.results.length === baseline.length &&
                      mismatch.results.every((result, index) =>
                        JSON.stringify(result.actual) === JSON.stringify(baseline[index].actual) && result.error === baseline[index].error &&
                        result.pass === (index === flippedIndex ? false : baseline[index].pass)) &&
                      mismatch.passed === baseline.filter(result => result.pass).length - 1;
                  }
                  if (data.schemaVersion === 3) {
                    const invalidProperty = structuredClone(data);
                    invalidProperty.property = "unsupported-property";
                    controls.propertyRejected = false;
                    try { await run(invalidProperty); } catch (error) {
                      controls.propertyRejected = String(error).includes("Unsupported computed fixture format");
                    }
                  }
                  if (data.stylesheetAdmission === true) {
                    const changed = structuredClone(data);
                    if (data.layerAdmission === true) { changed.scenarios[0].effectiveRules = []; }
                    else { changed.scenarios[0].effectiveDeclarations = []; }
                    controls.stylesheetSummaryRejected = false;
                    try { await run(changed); } catch (error) {
                      controls.stylesheetSummaryRejected = String(error).includes("Visibility stylesheet admission failed");
                    }
                    const rejected = structuredClone(data);
                    const scenario = rejected.scenarios[0];
                    if (!scenario.css.includes("visibility:visible")) {
                      throw new Error("Missing explicit default visibility control");
                    }
                    scenario.css = scenario.css.replace("visibility:visible", "visibility:unsupported-value");
                    for (const test of rejected.cases.filter(test => test.scenario === scenario.name)) {
                      test.css = scenario.css;
                    }
                    controls.rejectedVisibilityDetected = false;
                    try { await run(rejected); } catch (error) {
                      controls.rejectedVisibilityDetected = String(error).includes("Visibility stylesheet admission failed");
                    }
                    const wrongDocument = structuredClone(data);
                    wrongDocument.computedDocument.compatMode = "BackCompat";
                    controls.computedDocumentRejected = false;
                    try { await run(wrongDocument); } catch (error) {
                      controls.computedDocumentRejected = String(error).includes("Unsupported computed document profile");
                    }
                  }
                  let layerControlEvidence = null;
                  if (data.layerAdmission === true) {
                    const reordered = structuredClone(data);
                    const orderScenario = reordered.scenarios.find(scenario => scenario.name === "layer order admission control same result");
                    if (!orderScenario || !orderScenario.css.startsWith("@layer a,b;")) {
                      throw new Error("Missing layer order control fixture");
                    }
                    orderScenario.css = orderScenario.css.replace("@layer a,b;", "@layer b,a;");
                    for (const test of reordered.cases.filter(test => test.scenario === orderScenario.name)) { test.css = orderScenario.css; }
                    controls.layerOrderRejected = false;
                    try { await run(reordered); } catch (error) {
                      controls.layerOrderRejected = String(error).includes("Visibility stylesheet admission failed: layer rule structure");
                    }
                    const changedWinner = structuredClone(data);
                    const winnerScenario = changedWinner.scenarios.find(scenario => scenario.name === "layer normal later rank wins");
                    if (!winnerScenario || !winnerScenario.css.includes("visibility:hidden")) {
                      throw new Error("Missing layer winner control fixture");
                    }
                    winnerScenario.css = winnerScenario.css.replace("visibility:hidden", "visibility:visible");
                    winnerScenario.effectiveRules[1].children[0].declarations[0].value = "visible";
                    for (const test of changedWinner.cases.filter(test => test.scenario === winnerScenario.name)) { test.css = winnerScenario.css; }
                    const winnerResult = await run(changedWinner);
                    const selected = winnerResult.results.filter(result => result.scenario === winnerScenario.name);
                    controls.layerWinnerDetected = winnerResult.layerAdmissionVerified === true &&
                      selected.length === 1 && selected[0].error === null && selected[0].actual === "visible" &&
                      selected[0].expected === "hidden" && selected[0].pass === false &&
                      winnerResult.results.every(result => result.scenario === winnerScenario.name || result.pass);
                    layerControlEvidence = {
                      order: {scenario: orderScenario.name, css: orderScenario.css, phase: "admission", rejected: controls.layerOrderRejected},
                      winner: {scenario: winnerScenario.name, css: winnerScenario.css, admissionVerified: winnerResult.layerAdmissionVerified,
                        effectiveRules: winnerResult.sheets.find(sheet => sheet.name === winnerScenario.name).effectiveRules,
                        results: selected}
                    };
                  }
                  let conditionControlEvidence = null;
                  if (data.conditionAdmission === true) {
                    const changed = structuredClone(data);
                    const summaryScenario = changed.scenarios.find(scenario => scenario.name === "conditional condition control same computed result");
                    if (!summaryScenario) { throw new Error("Missing global condition control fixture"); }
                    summaryScenario.effectiveRules[1].conditionMatches = true;
                    controls.conditionTruthRejected = false;
                    try { await run(changed); } catch (error) {
                      controls.conditionTruthRejected = String(error).includes("Visibility stylesheet admission failed");
                    }
                    const sourceChanged = structuredClone(data);
                    const sourceScenario = sourceChanged.scenarios.find(scenario => scenario.name === summaryScenario.name);
                    sourceScenario.css = sourceScenario.css.replace("@media print", "@media screen");
                    sourceScenario.effectiveRules[1].conditionText = "screen";
                    for (const test of sourceChanged.cases.filter(test => test.scenario === sourceScenario.name)) { test.css = sourceScenario.css; }
                    controls.conditionSourceRejected = false;
                    try { await run(sourceChanged); } catch (error) {
                      controls.conditionSourceRejected = String(error).includes("Visibility stylesheet admission failed");
                    }
                    const changedWinner = structuredClone(data);
                    const winner = changedWinner.scenarios.find(scenario => scenario.name === "conditional screen active");
                    if (!winner) { throw new Error("Missing global condition winner fixture"); }
                    winner.css = winner.css.replace("@media screen", "@media print");
                    winner.effectiveRules[0].conditionText = "print";
                    winner.effectiveRules[0].conditionMatches = false;
                    for (const test of changedWinner.cases.filter(test => test.scenario === winner.name)) { test.css = winner.css; }
                    const changedResult = await run(changedWinner);
                    const selected = changedResult.results.filter(result => result.scenario === winner.name);
                    controls.conditionWinnerDetected = changedResult.conditionAdmissionVerified === true &&
                      selected.length === 1 && selected[0].error === null && selected[0].actual === "visible" &&
                      selected[0].expected === "hidden" && selected[0].pass === false &&
                      changedResult.results.every(result => result.scenario === winner.name || result.pass);
                    conditionControlEvidence = {
                      truth: {scenario: summaryScenario.name, phase: "admission", rejected: controls.conditionTruthRejected},
                      source: {scenario: sourceScenario.name, css: sourceScenario.css, phase: "admission", rejected: controls.conditionSourceRejected},
                      winner: {scenario: winner.name, css: winner.css, admissionVerified: changedResult.conditionAdmissionVerified,
                        effectiveRules: changedResult.sheets.find(sheet => sheet.name === winner.name).effectiveRules, results: selected}
                    };
                  }
                  if (data.opacityAdmission === true) {
                    const rejected = structuredClone(data);
                    const scenario = rejected.scenarios[0];
                    scenario.css = "#p{opacity:unsupported-value;}";
                    for (const test of rejected.cases.filter(test => test.scenario === scenario.name)) {
                      test.css = scenario.css;
                    }
                    controls.rejectedDeclarationDetected = false;
                    try { await run(rejected); } catch (error) {
                      controls.rejectedDeclarationDetected = String(error).includes("Opacity declaration admission failed");
                    }
                  }
                  if ([2, 4, 5, 6].includes(data.schemaVersion) || data.stylesheetAdmission === true) {
                    const reordered = structuredClone(data);
                    const parent = reordered.nodes.find(node =>
                      node.children?.filter(child => child.kind === "element").length >= 2);
                    if (!parent) { throw new Error("No child-order control fixture"); }
                    const indexes = parent.children.map((child, index) =>
                      child.kind === "element" ? index : -1).filter(index => index >= 0);
                    const [first, second] = indexes;
                    [parent.children[first], parent.children[second]] =
                      [parent.children[second], parent.children[first]];
                    controls.childOrderRejected = false;
                    try { await run(reordered); } catch (error) {
                      controls.childOrderRejected = String(error).includes("DOM snapshot mismatch:");
                    }
                  }
                  if (data.schemaVersion === 4) {
                    const changed = structuredClone(data);
                    const index = changed.cases.findIndex(test => test.name === "scope query direct child");
                    if (index < 0 || baseline[index].actual !== true) {
                      throw new Error("Missing passing scope receiver control");
                    }
                    changed.cases[index].node = changed.cases[index].candidate;
                    const rebound = await run(changed);
                    controls.scopeReceiverDetected = rebound.results.length === baseline.length &&
                      rebound.results.every((result, position) => result.error === baseline[position].error &&
                        result.actual === (position === index ? false : baseline[position].actual)) &&
                      rebound.results[index].pass === false;
                  }
                  if (data.schemaVersion === 5) {
                    const enumerated = structuredClone(data);
                    enumerated.nodes.reverse();
                    const reordered = await run(enumerated);
                    controls.enumerationIgnored = JSON.stringify(reordered.results) === JSON.stringify(baseline);
                    const changed = structuredClone(data);
                    const controlName = data.receiverControl?.caseName ?? "ordered query receiver children all";
                    const index = changed.cases.findIndex(test => test.name === controlName);
                    const leaf = changed.nodes.find(node => data.receiverControl ?
                      node.key === data.receiverControl.node : node.localName === "h1");
                    if (index < 0 || !leaf || baseline[index].actual.length !== 3) {
                      throw new Error("Missing ordered receiver control");
                    }
                    changed.cases[index].node = leaf.key;
                    const rebound = await run(changed);
                    controls.scopeReceiverDetected = rebound.results.length === baseline.length &&
                      rebound.results.every((result, position) => result.error === baseline[position].error &&
                        JSON.stringify(result.actual) === JSON.stringify(position === index ? [] : baseline[position].actual)) &&
                      rebound.results[index].pass === false;
                  }
                  if (data.schemaVersion === 6) {
                    const changed = structuredClone(data);
                    const index = changed.cases.findIndex(test => test.expectedError === "SyntaxError");
                    if (index < 0 || baseline[index].errorName !== "SyntaxError") {
                      throw new Error("Missing syntax rejection control");
                    }
                    changed.cases[index].css = ":nth-child(1)";
                    const accepted = await run(changed);
                    controls.syntaxRejectionDetected = accepted.results.length === baseline.length &&
                      accepted.results.every((result, position) => position === index ?
                        result.error === null && result.errorName === null && typeof result.actual === "boolean" && result.pass === false :
                        JSON.stringify(result) === JSON.stringify(baseline[position])) &&
                      accepted.passed === baseline.filter(result => result.pass).length - 1;
                  }
                  if (data.documentLanguage !== undefined) {
                    const swapped = structuredClone(data);
                    swapped.documentLanguage = data.documentLanguage === "html" ? "xml" : "html";
                    if (data.documentMode !== undefined) {
                      swapped.documentMode = "no-quirks";
                    }
                    const index = data.cases.findIndex(test => test.css === "*|DIV" && test.node === "htmlLower");
                    if (index < 0 || baseline[index].actual !== (data.documentLanguage === "html")) {
                      throw new Error("Missing document-language control");
                    }
                    const other = await run(swapped);
                    controls.documentLanguageDetected = other.results.length === baseline.length &&
                      other.results[index].error === null && other.results[index].actual === !baseline[index].actual &&
                      other.results[index].pass === false;
                    const changed = structuredClone(data);
                    changed.nodes.find(node => node.key === "nullUpper").namespaceURI = "urn:changed-type-head";
                    const nullIndex = data.cases.findIndex(test => test.css === "|P" && test.node === "nullUpper");
                    if (nullIndex < 0 || baseline[nullIndex].actual !== true) {
                      throw new Error("Missing namespace control");
                    }
                    const foreign = await run(changed);
                    controls.namespaceDetected = foreign.results.length === baseline.length &&
                      foreign.results[nullIndex].error === null && foreign.results[nullIndex].actual === false &&
                      foreign.results[nullIndex].pass === false;
                  }
                  if (data.documentMode !== undefined) {
                    const changed = structuredClone(data);
                    if (data.documentLanguage === "html") {
                      changed.documentMode = data.documentMode === "quirks" ? "no-quirks" : "quirks";
                      const index = data.cases.findIndex(test => test.css === "#a" && test.node === "htmlLower");
                      if (index < 0 || baseline[index].actual !== (data.documentMode === "quirks")) {
                        throw new Error("Missing identity document-mode control");
                      }
                      const other = await run(changed);
                      controls.documentModeDetected = other.results.length === baseline.length &&
                        other.results[index].error === null && other.results[index].actual === !baseline[index].actual &&
                        other.results[index].pass === false;
                    } else {
                      changed.documentMode = "quirks";
                      controls.invalidModeRejected = false;
                      try { await run(changed); } catch (error) {
                        controls.invalidModeRejected = String(error).includes("Invalid document-mode profile");
                      }
                    }
                  }
                  if (data.htmlStandardMode === true) {
                    const foreign = structuredClone(data);
                    foreign.nodes[0].namespaceURI = "urn:unsupported-selector-profile";
                    controls.htmlProfileRejected = false;
                    try { await run(foreign); } catch (error) {
                      controls.htmlProfileRejected = String(error).includes("HTML standards-mode profile mismatch");
                    }
                  }
                  return {...controls, layerControlEvidence, conditionControlEvidence};
                  })().then(done, error => done({harnessError: String(error)}));
                """,
                "args": [fixtures, browser["results"]], "newSandbox": True, "sandbox": "default",
                "line": 1, "filename": "browser_check.py",
            })
            controls = control_result.get("value", control_result)
            layer_control_evidence = controls.pop("layerControlEvidence", None)
            condition_control_evidence = controls.pop("conditionControlEvidence", None)
            expected_controls = {"snapshotRejected": True, "mismatchDetected": True}
            if fixtures["schemaVersion"] == 3:
                expected_controls["propertyRejected"] = True
            if fixtures.get("opacityAdmission") is True:
                expected_controls["rejectedDeclarationDetected"] = True
            if fixtures.get("stylesheetAdmission") is True:
                expected_controls.update(stylesheetSummaryRejected=True, rejectedVisibilityDetected=True,
                                         computedDocumentRejected=True)
            if fixtures["schemaVersion"] in (2, 4, 5, 6) or fixtures.get("stylesheetAdmission") is True:
                expected_controls["childOrderRejected"] = True
            if fixtures["schemaVersion"] == 4:
                expected_controls["scopeReceiverDetected"] = True
            if fixtures["schemaVersion"] == 5:
                expected_controls["enumerationIgnored"] = True
                expected_controls["scopeReceiverDetected"] = True
            if fixtures["schemaVersion"] == 6:
                expected_controls["syntaxRejectionDetected"] = True
            if fixtures.get("htmlStandardMode") is True:
                expected_controls["htmlProfileRejected"] = True
            if "documentLanguage" in fixtures:
                expected_controls["documentLanguageDetected"] = True
                expected_controls["namespaceDetected"] = True
            if "documentMode" in fixtures:
                expected_controls["documentModeDetected" if fixtures["documentLanguage"] == "html" else "invalidModeRejected"] = True
            if fixtures.get("layerAdmission") is True:
                expected_controls.update(layerOrderRejected=True, layerWinnerDetected=True)
            if fixtures.get("conditionAdmission") is True:
                expected_controls.update(conditionTruthRejected=True, conditionSourceRejected=True, conditionWinnerDetected=True)
            controls_passed = controls == expected_controls
            verify_sources()
            report = {"status": "pass" if passed == len(results) and controls_passed else "fail",
                      "session": session, "browser": browser, "command": command,
                      "negative_controls": controls,
                      "layer_control_evidence": layer_control_evidence,
                      "condition_control_evidence": condition_control_evidence,
                      "export_command": export_command, "fixture_suite": args.fixture_suite,
                      "proof_report_sha256": hashlib.sha256(proof_bytes).hexdigest(),
                      "fixtures_sha256": hashlib.sha256(exported.stdout.encode()).hexdigest(),
                      "source_sha256": source_hashes, "browser_refinement_proved": False}
            report_path.write_text(json.dumps(report, indent=2, sort_keys=True) + "\n")
            print(f"{report['status'].upper()}: {browser['passed']}/{browser['total']} browser cases")
            print(report_path)
            if not controls_passed:
                raise RuntimeError(f"Browser rejection controls failed: {controls}")
            if report["status"] != "pass":
                raise RuntimeError("Browser differential mismatch; see report")
        finally:
            if client is not None:
                try:
                    client.request("WebDriver:DeleteSession", {})
                except (OSError, RuntimeError):
                    pass
                client.close()
            if process.poll() is None:
                process.terminate()
                try:
                    process.wait(timeout=5)
                except subprocess.TimeoutExpired:
                    process.kill()
                    process.wait(timeout=5)


if __name__ == "__main__":
    main()
