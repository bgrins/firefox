import sys
from pathlib import Path
sys.dont_write_bytecode = True
ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "testing/web-platform/tests"))
from tools import localpaths
from wptrunner import wptrunner
if __name__ == "__main__":
    if '--check-args' in sys.argv:
        sys.argv.remove('--check-args')
        from wptrunner import wptcommandline
        kwargs = wptcommandline.parse_args()
        print({key: kwargs[key] for key in ['binary', 'run_info', 'prefs_root', 'manifest_update', 'manifest_download', 'config']})
        sys.exit(0)
    sys.exit(wptrunner.main())
