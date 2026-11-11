import hashlib
import json
from pathlib import Path
import subprocess
import urllib.request

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]


def sha(data):
    return hashlib.sha256(data).hexdigest()


def main():
    def git(*args):
        return subprocess.check_output(["git", "-c", "core.fsmonitor=false", *args], cwd=ROOT)
    revision = git("rev-parse", "HEAD").decode().strip()
    names = ["layout/style/GeckoBindings.cpp", "layout/style/GeckoBindings.h",
             "layout/style/nsAnimationManager.h", "dom/animation/CSSAnimation.cpp",
             "dom/animation/KeyframeEffect.cpp", "dom/animation/Keyframe.h",
             "servo/ports/geckolib/glue.rs", "servo/components/style/stylesheets/keyframes_rule.rs",
             "testing/web-platform/tests/scroll-animations/css/merge-timeline-offset-keyframes.html",
             "testing/web-platform/meta/scroll-animations/__dir__.ini"]
    files = {}
    for name in names:
        data = (ROOT / name).read_bytes()
        committed = git("show", revision + ":" + name)
        assert data == committed, name
        target = HERE / "source" / name
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_bytes(data)
        files[name] = sha(data)
    assert git("rev-parse", "HEAD").decode().strip() == revision
    (HERE / "SOURCES.json").write_text(json.dumps({"revision": revision, "files": files}, indent=2) + "\n")
    primary = {}
    for spec, url, section in [
        ("css-animations-2", "https://drafts.csswg.org/css-animations-2/", "css-processing.json"),
        ("scroll-animations-1", "https://drafts.csswg.org/scroll-animations-1/", "scroll-keyframes.json"),
        ("web-animations-1", "https://drafts.csswg.org/web-animations-1/", "getkeyframes.json")]:
        data = urllib.request.urlopen(url, timeout=60).read()
        target = HERE / "primary" / (spec + ".html")
        target.parent.mkdir(exist_ok=True)
        target.write_bytes(data)
        indexed = json.loads((HERE / section).read_text())
        primary[spec] = {"url": url, "sha256": sha(data), "indexed_sha": indexed["sha"],
                         "index_matches_html": indexed["sha"] == "hash:" + sha(data)}
    (HERE / "PRIMARY.json").write_text(json.dumps(primary, indent=2) + "\n")
    anchors = {}
    for anchor in ["CSS-ANIMATIONS-2#keyframe-processing", "CSS-ANIMATIONS-2#computed-keyframe-order",
                   "CSS-ANIMATIONS-2#used-keyframe-order", "SCROLL-ANIMATIONS-1#named-range-keyframes",
                   "WEB-ANIMATIONS-1#dom-keyframeeffect-getkeyframes"]:
        p = subprocess.run(["webspec-index", "exists", anchor], capture_output=True, text=True)
        assert p.returncode == 0, p.stderr
        anchors[anchor] = {"exit": p.returncode, "output": p.stdout, "stderr": p.stderr}
    (HERE / "ANCHORS.json").write_text(json.dumps(anchors, indent=2) + "\n")
    print(json.dumps({"revision": revision, "source_files": len(files), "primary": primary}))


if __name__ == "__main__":
    main()
