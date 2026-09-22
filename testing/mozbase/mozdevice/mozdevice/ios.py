# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this file,
# You can obtain one at http://mozilla.org/MPL/2.0/.

"""mozdevice.ios is an experimental, early stages abstraction layer for running
tests with Gecko on iOS devices. Currently this package only provides support
for running tests on simulator, and is not ready for general-purpose use."""

import json
import os
import re
import shutil
import subprocess
import sys
import tempfile
import time
from collections import namedtuple

from mozprocess import processhandler

# How RunningBoard logs the termination of an app or app extension process,
# e.g. "[app<org.example.App((null))>:1234] termination reported by launchd
# (2, 11, 11)", where 2 is the domain of signals and 11 the signal number.
TERMINATION_RE = re.compile(
    r"\[(?:app|xpcservice)<(?P<name>[^(>]+).*:(?P<pid>\d+)\] "
    r"termination reported by launchd \((?P<domain>\d+), (?P<code>\d+)"
)
SIGNAL_DOMAIN = 2


class ProcessTermination(namedtuple("ProcessTermination", "name pid domain code")):
    @property
    def signal(self):
        """The signal that terminated the process, or None if it exited."""
        return self.code if self.domain == SIGNAL_DOMAIN else None


class IosDevice:
    def __init__(self, uuid, name, is_simulator):
        self.uuid = uuid
        self.name = name
        self.is_simulator = is_simulator

    @staticmethod
    def all_devices(is_simulator):
        if is_simulator:
            return IosDeviceSimulator.all_devices()
        else:
            return IosDeviceReal.all_devices()

    @staticmethod
    def select_device(is_simulator, device_uuid=None):
        if device_uuid is None:
            device_uuid = os.environ.get("DEVICE_UUID", None)

        all_devices = IosDevice.all_devices(is_simulator)
        for device in all_devices:
            if device_uuid is not None:
                if device.uuid == device_uuid:
                    return device
            elif not device.is_simulator or device.state == "Booted":
                return device
        raise Exception(
            "Couldn't find a booted and connected iOS device with the correct platform"
        )


# FIXME: Does not have support for the features of IosDeviceSimulator, nor does it
# have the same API yet...
class IosDeviceReal(IosDevice):
    def __init__(self, uuid, name):
        super().__init__(uuid, name, False)

    def install(self, app_bundle):
        subprocess.check_call([
            "xcrun",
            "devicectl",
            "device",
            "install",
            "app",
            "--device",
            self.uuid,
            app_bundle,
        ])

    @staticmethod
    def all_devices():
        with tempfile.NamedTemporaryFile() as tmpfile:
            subprocess.check_call(
                ["xcrun", "devicectl", "list", "devices", "-j", tmpfile.name],
                stdout=subprocess.DEVNULL,
            )
            output = json.load(tmpfile)

        if output["info"]["outcome"] != "success":
            sys.stderr.write("Failed to read device list")
            return []

        return [
            IosDeviceReal(device["identifier"], device["deviceProperties"]["name"])
            for device in output["result"]["devices"]
        ]


class IosDeviceSimulator(IosDevice):
    def __init__(self, uuid, name, runtime, datapath, logpath, state):
        super().__init__(uuid, name, True)
        self.runtime = runtime
        self.datapath = datapath
        self.logpath = logpath
        self.state = state

    def install(self, app_bundle):
        subprocess.check_call(["xcrun", "simctl", "install", self.uuid, app_bundle])

    def xcode_destination_specifier(self):
        return "platform=iOS simulator,id=" + self.uuid

    def launch_process(
        self,
        bundle_id,
        args=[],
        env=None,
        wait_for_debugger=False,
        terminate_running_process=True,
        **kwargs,
    ):
        # Put provided environment variables in `SIMCTL_CHILD_` so they
        # propagate into the simulator.
        kwargs["env"] = os.environ.copy()
        if env:
            for name, value in env.items():
                kwargs["env"]["SIMCTL_CHILD_" + name] = value

        # Specify provided flags
        extra_args = []
        if wait_for_debugger:
            extra_args += ["--wait-for-debugger"]
        if terminate_running_process:
            extra_args += ["--terminate-running-process"]

        # XXX: this should perhaps capture stdout/stderr with
        # `--stdout/--stderr` rather than `--console`?

        # FIXME: the ProcessHandlerMixin will have the pid for the xcrun
        # command, not the actual app, which isn't great for debugging.

        return processhandler.ProcessHandlerMixin(
            [
                "xcrun",
                "simctl",
                "launch",
                *extra_args,
                "--console",
                self.uuid,
                bundle_id,
                *args,
            ],
            **kwargs,
        )

    def test_root(self, bundle_id):
        container_path = subprocess.check_output(
            [
                "xcrun",
                "simctl",
                "get_app_container",
                self.uuid,
                bundle_id,
                "data",
            ],
            text=True,
        )
        return os.path.join(container_path.strip(), "test_root")

    def rm(self, path, force=False, recursive=False):
        try:
            if recursive:
                shutil.rmtree(path, ignore_errors=True)
            else:
                os.remove(path)
        except Exception:
            pass

    def mkdir(self, path, parents=False):
        if parents:
            os.makedirs(path, exist_ok=True)
        else:
            os.mkdir(path)

    def push(self, local, remote):
        shutil.copytree(local, remote, dirs_exist_ok=True)

    def pull(self, remote, local):
        shutil.copytree(remote, local, dirs_exist_ok=True)

    def chmod(self, path, recursive=False, mask="777"):
        if recursive:
            for root, dirs, files in os.walk(path):
                for d in dirs:
                    os.chmod(os.path.join(root, d), int(mask, 8))
                for f in files:
                    os.chmod(os.path.join(root, f), int(mask, 8))
        else:
            os.chmod(path, int(mask, 8))

    def is_file(self, path):
        return os.path.isfile(path)

    def is_dir(self, path):
        return os.path.isdir(path)

    def get_file(self, path, offset=None, length=None):
        with open(path, mode="rb") as f:
            if offset is not None and length is not None:
                f.seek(offset)
                return f.read(length)
            if offset is not None:
                f.seek(offset)
                return f.read()
            return f.read()

    def stop_application(self, bundle_id):
        try:
            subprocess.check_call([
                "xcrun",
                "simctl",
                "terminate",
                self.uuid,
                bundle_id,
            ])
        except subprocess.CalledProcessError:
            pass

    def crash_reports(self, since, report_dir=None):
        """Return the crash reports written since the time `since` for processes
        running in this simulator, oldest first. Simulator processes are host
        processes, so the host writes their reports, in the .ips format: a line
        of JSON metadata followed by the JSON report, which is what's returned,
        with its path added under "path"."""
        report_dir = report_dir or os.path.expanduser(
            "~/Library/Logs/DiagnosticReports"
        )
        try:
            names = os.listdir(report_dir)
        except FileNotFoundError:
            return []

        reports = []
        for name in names:
            path = os.path.join(report_dir, name)
            if not name.endswith(".ips") or os.path.getmtime(path) < since:
                continue
            try:
                with open(path, encoding="utf-8") as fh:
                    fh.readline()
                    report = json.load(fh)
            except (OSError, ValueError):
                continue
            if f"/Devices/{self.uuid}/" not in report.get("procPath", ""):
                continue
            report["path"] = path
            reports.append(report)
        return sorted(reports, key=lambda r: os.path.getmtime(r["path"]))

    def crash_report(self, pid, since, timeout=0):
        """Return the crash report of the process `pid` written since the time
        `since`, waiting up to `timeout` seconds for the host to write it, or
        None. The host doesn't write reports for every crash."""
        deadline = time.time() + timeout
        while True:
            for report in self.crash_reports(since):
                if report.get("pid") == pid:
                    return report
            if time.time() >= deadline:
                return None
            time.sleep(1)

    def process_terminations(self, since, bundle_id):
        """Return how the processes of the app `bundle_id` and of its extensions
        that ended since the time `since` terminated, according to launchd."""
        start = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(since))
        predicate = (
            'process == "runningboardd" AND '
            'eventMessage CONTAINS "termination reported by launchd" AND '
            f'eventMessage CONTAINS "{bundle_id}"'
        )
        output = subprocess.check_output(
            [
                "xcrun",
                "simctl",
                "spawn",
                self.uuid,
                "log",
                "show",
                "--start",
                start,
                "--style",
                "compact",
                "--predicate",
                predicate,
            ],
            text=True,
        )
        terminations = []
        for line in output.splitlines():
            if match := TERMINATION_RE.search(line):
                terminations.append(
                    ProcessTermination(
                        match["name"],
                        int(match["pid"]),
                        int(match["domain"]),
                        int(match["code"]),
                    )
                )
        return terminations

    @staticmethod
    def all_devices():
        output = json.loads(
            subprocess.check_output(["xcrun", "simctl", "list", "devices", "-j"])
        )

        result = []
        for runtime, devices in output["devices"].items():
            for device in devices:
                if not device["isAvailable"]:
                    continue
                result.append(
                    IosDeviceSimulator(
                        device["udid"],
                        device["name"],
                        runtime,
                        device["dataPath"],
                        device["logPath"],
                        device["state"],
                    )
                )
        return result
