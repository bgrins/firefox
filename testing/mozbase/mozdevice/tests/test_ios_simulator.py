#!/usr/bin/env python

import json
import os
import signal
from unittest import mock

import mozunit
from mozdevice.ios import IosDeviceSimulator

UUID = "1420CEFE-C4A9-485C-A91C-B61B69F4588C"

# Lines `log show` printed for an app killed by SIGSEGV, whose content process
# then exited normally.
LOG = """\
2026-09-21 22:42:45.372 Df runningboardd[35931:4c305bd] [com.apple.runningboard:ttl] [app<org.mozilla.ios.GeckoTestBrowser((null))>:64457] termination reported by launchd (2, 11, 11)
2026-09-21 22:42:45.373 Df runningboardd[35931:4c305c0] [com.apple.runningboard:ttl] [xpcservice<org.mozilla.ios.GeckoTestBrowser.WebContent([app<org.mozilla.ios.GeckoTestBrowser((null))>:64457])>{vt hash: 266576133}[uuid:6E0A7D26-42C1-AE1D-A1C6EE67C459]{definition:org.mozilla.ios.GeckoTestBrowser.WebContent[extension][client]}:64463] termination reported by launchd (0, 0, 0)
"""


def simulator():
    return IosDeviceSimulator(UUID, "iPhone", "iOS-26-3", "", "", "Booted")


def test_process_terminations():
    with mock.patch("subprocess.check_output", return_value=LOG):
        terminations = simulator().process_terminations(
            0, "org.mozilla.ios.GeckoTestBrowser"
        )

    assert [(t.name, t.pid, t.signal) for t in terminations] == [
        ("org.mozilla.ios.GeckoTestBrowser", 64457, signal.SIGSEGV),
        ("org.mozilla.ios.GeckoTestBrowser.WebContent", 64463, None),
    ]


def write_report(directory, name, pid, device, mtime):
    path = os.path.join(directory, name)
    with open(path, "w", encoding="utf-8") as fh:
        fh.write(json.dumps({"app_name": "GeckoTestBrowser"}) + "\n")
        proc_path = f"/Users/USER/Library/Developer/CoreSimulator/Devices/{device}/data/GeckoTestBrowser.app/GeckoTestBrowser"
        fh.write(json.dumps({"pid": pid, "procPath": proc_path}))
    os.utime(path, (mtime, mtime))


def test_crash_reports(tmp_path):
    write_report(tmp_path, "old.ips", 1, UUID, 100)
    write_report(tmp_path, "other-device.ips", 2, "OTHER-DEVICE", 300)
    write_report(tmp_path, "crash.ips", 3, UUID, 300)

    reports = simulator().crash_reports(200, report_dir=str(tmp_path))

    assert [report["pid"] for report in reports] == [3]


if __name__ == "__main__":
    mozunit.main()
