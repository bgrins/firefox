# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at http://mozilla.org/MPL/2.0/.

# Run xpcshell tests in the iOS Simulator. Simulator processes run on the host
# and see its file system, so the desktop harness works unchanged, except that
# xpcshell has to be started through `simctl spawn`. That only passes on
# environment variables prefixed with SIMCTL_CHILD_, and doesn't keep the
# working directory, which ios-sim-launcher restores.

import runxpcshelltests

# Prefixes of the environment variables the harness sets for xpcshell.
FORWARDED_PREFIXES = (
    "JS_",
    "MOZ_",
    "MOZILLA_",
    "NSPR_",
    "RUST_",
    "XPCOM_",
    "XPCSHELL_",
    "XRE_",
)


class IOSSimulatorXPCShellTestThread(runxpcshelltests.XPCShellTestThread):
    def __init__(self, *args, **kwargs):
        runxpcshelltests.XPCShellTestThread.__init__(self, *args, **kwargs)
        mobile_args = kwargs["mobileArgs"]
        self.device_uuid = mobile_args["device_uuid"]
        self.launcher = mobile_args["launcher"]

    def launchProcess(
        self, cmd, stdout, stderr, env, cwd, timeout=None, test_name=None
    ):
        spawn_env = dict(env)
        for name, value in env.items():
            if name.startswith(FORWARDED_PREFIXES):
                spawn_env["SIMCTL_CHILD_" + name] = value
        spawn_env["SIMCTL_CHILD_IOS_SIM_CWD"] = cwd
        cmd = ["xcrun", "simctl", "spawn", self.device_uuid, self.launcher] + cmd
        return runxpcshelltests.XPCShellTestThread.launchProcess(
            self, cmd, stdout, stderr, spawn_env, cwd, timeout, test_name
        )
