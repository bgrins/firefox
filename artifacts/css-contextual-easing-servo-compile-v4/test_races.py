from pathlib import Path
import runpy
import signal
import tempfile
from types import SimpleNamespace
import unittest
from unittest.mock import Mock, patch

HERE = Path(__file__).resolve().parent
runner = runpy.run_path(str(HERE / 'run.py'))


class ResourceRaceTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory(dir=HERE, prefix='race-test-')
        self.addCleanup(self.temp.cleanup)
        self.directory = Path(self.temp.name)
        self.kept = self.directory / 'kept'
        self.kept.write_bytes(b'kept data')
        self.entries = [(str(self.directory), [], ['gone', 'kept'])]

    def test_poll_skips_vanished_file_and_counts_remaining_files(self):
        info = self.kept.stat()
        with patch('os.walk', return_value=self.entries):
            result = runner['resources'](self.directory, self.directory, allow_missing=True)
        self.assertEqual(result['target_bytes'], max(info.st_size, info.st_blocks * 512))

    def test_post_exit_sample_rejects_vanished_file(self):
        with patch('os.walk', return_value=self.entries):
            with self.assertRaises(FileNotFoundError):
                runner['resources'](self.directory, self.directory)

    def test_poll_does_not_swallow_permission_error(self):
        original = Path.lstat

        def disappearing(path):
            if path.name == 'gone':
                raise PermissionError('simulated denial')
            return original(path)

        with patch('os.walk', return_value=self.entries), patch.object(Path, 'lstat', disappearing):
            with self.assertRaises(PermissionError):
                runner['resources'](self.directory, self.directory, allow_missing=True)


class ProcessGroupRaceTests(unittest.TestCase):
    def process(self):
        return SimpleNamespace(pid=12345, wait=Mock(return_value=0), poll=Mock(return_value=0))

    def test_group_disappears_between_probe_and_signal(self):
        process = self.process()
        with patch('os.killpg', side_effect=[None, ProcessLookupError(), ProcessLookupError()]) as kill:
            runner['stop_group'](process)
        process.wait.assert_called_once_with(timeout=1)
        self.assertEqual([call.args for call in kill.call_args_list],
                         [(process.pid, 0), (process.pid, signal.SIGTERM), (process.pid, 0)])

    def test_already_absent_group_is_waited_and_rechecked(self):
        process = self.process()
        with patch('os.killpg', side_effect=ProcessLookupError()) as kill:
            runner['stop_group'](process)
        process.wait.assert_called_once_with(timeout=1)
        self.assertEqual([call.args for call in kill.call_args_list],
                         [(process.pid, 0), (process.pid, 0)])

    def test_signal_permission_failure_is_not_swallowed(self):
        process = self.process()
        with patch('os.killpg', side_effect=[None, PermissionError('simulated denial')]):
            with self.assertRaises(PermissionError):
                runner['stop_group'](process)


if __name__ == '__main__':
    unittest.main(verbosity=2)
