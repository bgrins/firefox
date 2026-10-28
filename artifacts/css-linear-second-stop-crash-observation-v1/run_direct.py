import hashlib
import json
import os
from pathlib import Path
import shutil
import signal
import subprocess
import tempfile
import time

HERE = Path(__file__).resolve().parent
BINARY = Path('/Applications/Firefox.app/Contents/MacOS/firefox')
OUT = HERE / 'direct-release'
OUT.mkdir()
cases = {
    'control': 'linear(0 calc(sibling-index() * 1%), 1)',
    'second-position': 'linear(0 0% calc(sibling-index() * 1%), 1)',
}


def save(path, value):
    path.write_text(json.dumps(value, indent=2, sort_keys=True) + '\n')


def members(group):
    rows = subprocess.check_output(['ps', '-axo', 'pid=,pgid=,stat='], text=True)
    return [line.strip() for line in rows.splitlines()
            if len(line.split()) == 3 and int(line.split()[1]) == group
            and not line.split()[2].startswith('Z')]


for label, value in cases.items():
    directory = OUT / label
    directory.mkdir()
    html = '<!doctype html><meta charset=utf-8><title>linear parser probe</title><body><script>\n'
    html += 'dump("LINEAR_PROBE_START\\n");\n'
    html += 'const element = document.createElement("i"); document.body.append(element);\n'
    html += 'element.style.setProperty("animation-timing-function", ' + json.dumps(value) + ');\n'
    html += 'dump("LINEAR_PROBE_RETURN " + JSON.stringify(element.style.animationTimingFunction) + "\\n");\n'
    html += '</script>\n'
    page = directory / 'probe.html'
    page.write_text(html)
    profile = Path(tempfile.mkdtemp(prefix='css-linear-stop-', dir='/private/tmp'))
    identity = [profile.stat().st_dev, profile.stat().st_ino]
    prefs = {
        'browser.dom.window.dump.enabled': True,
        'browser.shell.checkDefaultBrowser': False,
        'browser.aboutwelcome.enabled': False,
        'browser.startup.page': 0,
        'browser.startup.homepage_override.mstone': 'ignore',
        'startup.homepage_welcome_url': '',
        'browser.tabs.crashReporting.sendReport': False,
    }
    (profile / 'user.js').write_text(''.join(
        'user_pref(' + json.dumps(k) + ', ' + json.dumps(v) + ');\n'
        for k, v in prefs.items()))
    command = [str(BINARY), '-headless', '-no-remote', '-profile', str(profile), page.as_uri()]
    env = dict(os.environ, MOZ_CRASHREPORTER_DISABLE='1', MOZ_CRASHREPORTER_NO_REPORT='1',
               MOZ_CRASHREPORTER_SHUTDOWN='1', RUST_BACKTRACE='1')
    process = None
    try:
        with (directory / 'browser.log').open('xb') as log:
            process = subprocess.Popen(command, stdout=log, stderr=subprocess.STDOUT,
                                       env=env, start_new_session=True)
            save(directory / 'PROCESS.json', {'pid': process.pid, 'group': process.pid,
                'command': command, 'profile_identity': identity, 'preferences': prefs})
            deadline = time.monotonic() + 20
            observed = ''
            while time.monotonic() < deadline:
                observed = (directory / 'browser.log').read_text(errors='replace')
                if 'LINEAR_PROBE_RETURN' in observed or 'panicked at' in observed or process.poll() is not None:
                    break
                time.sleep(0.1)
            before_cleanup = process.poll()
            save(directory / 'OBSERVATION.json', {
                'start_seen': 'LINEAR_PROBE_START' in observed,
                'return_seen': 'LINEAR_PROBE_RETURN' in observed,
                'panic_seen': 'panicked at' in observed,
                'exit_before_cleanup': before_cleanup,
                'observation_deadline_reached': time.monotonic() >= deadline,
            })
    finally:
        if process is not None:
            for sig in (signal.SIGTERM, signal.SIGKILL):
                if not members(process.pid):
                    break
                try:
                    os.killpg(process.pid, sig)
                except ProcessLookupError:
                    pass
                deadline = time.monotonic() + 3
                while members(process.pid) and time.monotonic() < deadline:
                    process.poll()
                    time.sleep(0.1)
            process.wait(timeout=3)
            assert not members(process.pid), 'owned browser group remains'
        assert not profile.is_symlink()
        assert [profile.stat().st_dev, profile.stat().st_ino] == identity
        shutil.rmtree(profile)
        save(directory / 'CLEANUP.json', {'owned_group_absent': process is None or not members(process.pid),
            'profile_removed': not profile.exists(), 'exit_after_cleanup': None if process is None else process.returncode})
    body = (directory / 'browser.log').read_bytes()
    save(directory / 'LOG.json', {'sha256': hashlib.sha256(body).hexdigest(), 'bytes': len(body)})
    print(label, (directory / 'OBSERVATION.json').read_text(), flush=True)
