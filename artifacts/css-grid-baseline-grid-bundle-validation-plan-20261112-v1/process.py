import json
import os
import signal
import subprocess
import time


def absent(pgid):
    if not isinstance(pgid, int) or isinstance(pgid, bool) or pgid <= 1:
        raise ValueError('Invalid owned process group')
    result = subprocess.run(['ps', '-axo', 'pid=,pgid=,command='],
                            capture_output=True, text=True, check=True, timeout=10)
    rows = [line.strip().split(None, 2) for line in result.stdout.splitlines()]
    if not rows or any(len(row) < 2 or not row[0].isdigit() or
                       not row[1].isdigit() for row in rows):
        raise RuntimeError('Cannot inspect owned process group')
    return not any(int(row[1]) == pgid for row in rows)



class Runner:
    def __init__(self, out):
        self.out = out
        self.commands = []
        self.groups = []
        self.safe_cleanup = True
        self.uncertain = False

    def run(self, argv, cwd, env, label, timeout=180):
        self.safe_cleanup = False
        record = dict(argv=argv, cwd=str(cwd), label=label)
        self.commands.append(record)
        path = self.out / (label + '.log')
        proc = None
        uncertain = False
        started = time.monotonic()
        try:
            with path.open('xb') as log:
                proc = subprocess.Popen(argv, cwd=cwd, env=env, stdout=log,
                                        stderr=subprocess.STDOUT, start_new_session=True)
                if proc.pid <= 1 or proc.pid == os.getpgrp():
                    raise RuntimeError('Invalid child group')
                self.groups.append(proc.pid)
                record['pgid'] = proc.pid
                try:
                    record['exit'] = proc.wait(timeout=timeout)
                except subprocess.TimeoutExpired:
                    record['timeout'] = True
                except BaseException:
                    uncertain = True
                    raise
                finally:
                    needs_stop = True
                    try:
                        needs_stop = not absent(proc.pid)
                    except BaseException as error:
                        uncertain = True
                        record['inspection_error'] = repr(error)
                    if needs_stop:
                        try:
                            try:
                                os.killpg(proc.pid, signal.SIGTERM)
                            except ProcessLookupError:
                                pass
                            try:
                                proc.wait(timeout=5)
                            except subprocess.TimeoutExpired:
                                try:
                                    os.killpg(proc.pid, signal.SIGKILL)
                                except ProcessLookupError:
                                    pass
                                proc.wait(timeout=5)
                        except BaseException as error:
                            uncertain = True
                            record['stop_error'] = repr(error)
                    try:
                        record['group_absent'] = absent(proc.pid)
                        earlier_absent = all(absent(group) for group in self.groups)
                        self.uncertain = self.uncertain or uncertain
                        self.safe_cleanup = not self.uncertain and record['group_absent'] and earlier_absent
                    except BaseException as error:
                        uncertain = True
                        self.safe_cleanup = False
                        self.uncertain = True
                        record['final_inspection_error'] = repr(error)
        except BaseException as error:
            self.safe_cleanup = False
            self.uncertain = True
            record['error'] = repr(error)
            raise
        finally:
            record['seconds'] = time.monotonic() - started
            record['safe_cleanup'] = self.safe_cleanup
            (self.out / 'COMMANDS.json').write_text(json.dumps(self.commands, indent=2) + '\n')
        if not self.safe_cleanup or record.get('timeout') or 'exit' not in record:
            raise RuntimeError('Command failed lifecycle gate')
        return record, None
