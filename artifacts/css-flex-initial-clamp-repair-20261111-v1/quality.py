import json
import os
from pathlib import Path
import runpy
import sys
HERE=Path(__file__).resolve().parent
ROOT=HERE.parents[1]
stage=sys.argv[1]
assert stage in ["format", "lint"]
out=HERE/stage
out.mkdir()
argv=["/Users/bgrins/venvs/firefox/bin/python", "./mach", stage, "-l", "clang-format", "-l", "eslint", "-l", "stylelint", "-j", "1", "layout/generic/nsFlexContainerFrame.cpp", "dom/flex/test/chrome/test_flex_item_initial_clamp.html", "dom/flex/test/chrome.toml"]
(out/"COMMAND.json").write_text(json.dumps(argv,indent=2)+"\n")
env=dict(os.environ,MOZ_SKIP_PATH_PERFORMANCE_CHECK="1",MOZCONFIG=str(ROOT/"mozconfig"),MOZ_OBJDIR=str(ROOT/"objdir-full.noindex"),GIT_OPTIONAL_LOCKS="0")
runner=runpy.run_path(str(HERE/"process.py"))["Runner"](out)
record,_=runner.run(argv,ROOT,env,stage,timeout=180)
print(json.dumps(record))
sys.exit(record["exit"])
