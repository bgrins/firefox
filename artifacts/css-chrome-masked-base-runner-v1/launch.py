import json
import os
from pathlib import Path
import sys


def bootstrap(root):
    sys.dont_write_bytecode = True
    for name in ["mozprocess", "mozinfo", "mozlog", "mozrunner", "mozprofile", "mozdevice",
                 "mozfile", "moznetwork", "mozversion", "mozcrash", "mozdebug", "mozshellutil"]:
        sys.path.insert(0, str(root / "testing/mozbase" / name))
    for name in ["requests", "urllib3", "idna", "charset_normalizer"]:
        sys.path.insert(0, str(root / "third_party/python" / name))
    sys.path.insert(0, str(root / "python/mozterm"))
    sys.path.insert(0, str(root / "testing/web-platform/tests"))
    sys.path.insert(0, str(root / "testing/web-platform/tests/tools"))
    import localpaths
    from wptrunner import wptrunner, wptcommandline
    from wptrunner.browsers import chrome
    return wptrunner, wptcommandline, chrome


def filter_args(args):
    prefixes = ("--enable-features=", "--enable-blink-features=", "--enable-experimental-",
                "--enable-blink-test-features", "--enable-unsafe-", "--webtransport-developer-mode",
                "--ignore-certificate-errors", "--ip-address-space-overrides=", "--disable-features=")
    assert not any(a == "--no-sandbox" or a.startswith("--disable-sandbox") for a in args)
    return [a for a in args if not a.startswith(prefixes)]


def main():
    root = Path(os.environ["DURATION_RUNNER_ROOT"])
    runner, commandline, chrome = bootstrap(root)
    original = chrome.executor_kwargs

    def executor_kwargs(*args, **kwargs):
        result = original(*args, **kwargs)
        options = result["capabilities"]["goog:chromeOptions"]
        generated = list(options["args"])
        options["args"] = filter_args(generated)
        with open(os.environ["DURATION_CAPABILITIES"], "a") as stream:
            stream.write(json.dumps({"generated_args": generated, "effective_capabilities": result["capabilities"]}) + "\n")
        return result

    chrome.executor_kwargs = executor_kwargs
    return runner.main()


if __name__ == "__main__":
    raise SystemExit(main())
