import datetime
import hashlib
import json
from pathlib import Path
import urllib.request

root = Path(__file__).resolve().parent
configs = [
    ("css", "w3c/csswg-drafts", "css-syntax-3/Overview.bs"),
    ("infra", "whatwg/infra", "infra.bs"),
    ("webidl", "whatwg/webidl", "index.bs"),
    ("cssom", "w3c/csswg-drafts", "cssom-1/Overview.bs"),
    ("ecma", "tc39/ecma262", "spec.html"),
]
records = {}
for name, repo, path in configs:
    url = "https://api.github.com/repos/" + repo + "/commits?path=" + path + "&per_page=1"
    request = urllib.request.Request(url, headers={"User-Agent": "css-formal-research"})
    data = json.loads(urllib.request.urlopen(request).read())[0]
    revision = data["sha"]
    source = "https://raw.githubusercontent.com/" + repo + "/" + revision + "/" + path
    content = urllib.request.urlopen(source).read()
    destination = "inputs/" + name + (".html" if name == "ecma" else ".bs")
    (root / destination).write_bytes(content)
    records[name] = {"repository": repo, "path": path, "revision": revision,
                     "url": source, "file": destination,
                     "sha256": hashlib.sha256(content).hexdigest(),
                     "last_path_commit": data["commit"]["committer"]["date"]}
    print(name, revision, len(content))
(root / "SOURCES.json").write_text(json.dumps({
    "retrieved_utc": datetime.datetime.now(datetime.timezone.utc).isoformat(),
    "selection": "latest commit touching path at retrieval", "sources": records,
}, indent=2) + "\n")
