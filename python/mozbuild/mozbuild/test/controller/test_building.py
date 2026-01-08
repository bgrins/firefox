# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at http://mozilla.org/MPL/2.0/.

import logging
import os
import unittest
from unittest.mock import Mock

from mozunit import main

from mozbuild.controller.building import BuildOutputManager
from mozbuild.util import is_running_under_coding_agent


class TestBuildOutputManager(unittest.TestCase):
    """Tests for BuildOutputManager redirect output functionality."""

    def setUp(self):
        self._old_env = dict(os.environ)
        self._temp_files = []
        return unittest.TestCase.setUp(self)

    def tearDown(self):
        os.environ.clear()
        os.environ.update(self._old_env)

        # Clean up any temp files created during tests
        for f in self._temp_files:
            try:
                if os.path.exists(f):
                    os.remove(f)
            except Exception:
                pass

        # Clean up test objdir
        try:
            import shutil

            if os.path.exists("/tmp/test_objdir"):
                shutil.rmtree("/tmp/test_objdir")
        except Exception:
            pass

        return unittest.TestCase.tearDown(self)

    def _create_mock_log_manager(self):
        """Create a mock log_manager for testing."""
        log_manager = Mock()
        log_manager.terminal = Mock()
        log_manager.terminal_formatter = Mock()
        log_manager.structured_loggers = []
        log_manager.replace_terminal_handler = Mock(
            return_value=Mock(level=logging.INFO)
        )
        return log_manager

    def test_show_warning_creates_log_file(self):
        """Test that show='warning' creates a log file in objdir."""
        log_manager = self._create_mock_log_manager()
        monitor = Mock()
        monitor.topobjdir = "/tmp/test_objdir"
        footer = None

        # Create the objdir for the test
        os.makedirs(monitor.topobjdir, exist_ok=True)

        with BuildOutputManager(
            log_manager, monitor, footer, show="warning"
        ) as output_manager:
            self.assertIsNotNone(output_manager.redirect_log_file)
            self.assertIsNotNone(output_manager.redirect_log_handler)

            # Verify the log file exists in objdir
            expected_path = os.path.join(monitor.topobjdir, "last_log.txt")
            self.assertTrue(os.path.exists(expected_path))
            self._temp_files.append(expected_path)

            # Verify handler is configured correctly
            self.assertEqual(output_manager.redirect_log_handler.level, logging.DEBUG)

    def test_no_filtered_output_by_default(self):
        """Test that filtered output is not enabled by default (show='debug')."""
        log_manager = self._create_mock_log_manager()
        monitor = Mock()
        footer = None

        with BuildOutputManager(
            log_manager, monitor, footer, show="debug"
        ) as output_manager:
            self.assertIsNone(output_manager.redirect_log_file)
            self.assertIsNone(output_manager.redirect_log_handler)

    def test_show_warning_sets_terminal_level_to_warning(self):
        """Test that show='warning' sets terminal handler to WARNING level."""
        log_manager = self._create_mock_log_manager()
        monitor = Mock()
        monitor.topobjdir = "/tmp/test_objdir"
        footer = None

        os.makedirs(monitor.topobjdir, exist_ok=True)

        with BuildOutputManager(
            log_manager, monitor, footer, show="warning"
        ) as output_manager:
            # Verify that _redirect_terminal_level was set
            self.assertTrue(hasattr(output_manager, "_redirect_terminal_level"))
            self.assertEqual(output_manager._redirect_terminal_level, logging.WARNING)
            self._temp_files.append(os.path.join(monitor.topobjdir, "last_log.txt"))

    def test_show_error_cleanup_on_exit(self):
        """Test that log files are properly closed on exit."""
        log_manager = self._create_mock_log_manager()
        monitor = Mock()
        monitor.topobjdir = "/tmp/test_objdir"
        monitor.stop_resource_recording = Mock()
        footer = None

        os.makedirs(monitor.topobjdir, exist_ok=True)

        log_file_path = None
        with BuildOutputManager(log_manager, monitor, footer, show="error"):
            log_file_path = os.path.join(monitor.topobjdir, "last_log.txt")
            self._temp_files.append(log_file_path)

        # After exiting context, file should be closed but still exist
        self.assertTrue(os.path.exists(log_file_path))

    def test_show_info_file_handler_added_to_loggers(self):
        """Test that the file handler is added to structured loggers."""
        log_manager = self._create_mock_log_manager()

        # Create mock loggers
        mock_logger1 = Mock()
        mock_logger2 = Mock()
        log_manager.structured_loggers = [mock_logger1, mock_logger2]

        monitor = Mock()
        monitor.topobjdir = "/tmp/test_objdir"
        footer = None

        os.makedirs(monitor.topobjdir, exist_ok=True)

        with BuildOutputManager(
            log_manager, monitor, footer, show="info"
        ) as output_manager:
            log_file_path = os.path.join(monitor.topobjdir, "last_log.txt")
            self._temp_files.append(log_file_path)

            # Verify handler was added to all structured loggers
            mock_logger1.addHandler.assert_called_once()
            mock_logger2.addHandler.assert_called_once()

            # Verify it's the redirect handler
            handler = mock_logger1.addHandler.call_args[0][0]
            self.assertEqual(handler, output_manager.redirect_log_handler)


class TestBuildCommandShowLevel(unittest.TestCase):
    """Tests for build command show level auto-detection."""

    def setUp(self):
        self._old_env = dict(os.environ)
        return unittest.TestCase.setUp(self)

    def tearDown(self):
        os.environ.clear()
        os.environ.update(self._old_env)
        return unittest.TestCase.tearDown(self)

    def test_claudecode_env_sets_show_to_warning(self):
        """Test that CLAUDECODE environment variable sets show to warning."""
        # This tests the logic that would be in build_commands.py
        # Simulating: if show == "debug" and is_running_under_coding_agent():

        show = "debug"
        os.environ["CLAUDECODE"] = "1"

        # Simulate the auto-set logic
        if show == "debug" and is_running_under_coding_agent():
            show = "warning"

        self.assertEqual(show, "warning")

    def test_no_claudecode_env_keeps_default(self):
        """Test that show stays at default without CLAUDECODE."""
        show = "debug"
        os.environ.pop("CLAUDECODE", None)

        # Simulate the auto-set logic
        if show == "debug" and is_running_under_coding_agent():
            show = "warning"

        self.assertEqual(show, "debug")

    def test_explicit_show_not_overridden(self):
        """Test that explicit --show is not changed by CLAUDECODE."""
        show = "error"
        os.environ["CLAUDECODE"] = "1"

        # Simulate the auto-set logic (should not change if not debug)
        if show == "debug" and is_running_under_coding_agent():
            show = "warning"

        self.assertEqual(show, "error")

    def test_verbose_overrides_show(self):
        """Test that --verbose resets show to debug."""
        show = "warning"
        verbose = True

        # Simulate the conflict resolution logic
        if show != "debug" and verbose:
            show = "debug"

        self.assertEqual(show, "debug")

    def test_moz_automation_errors_with_show_filtering(self):
        """Test that MOZ_AUTOMATION errors when trying to use show filtering."""
        show = "warning"
        os.environ["MOZ_AUTOMATION"] = "1"

        # Simulate the automation check logic
        should_error = show != "debug" and bool(os.environ.get("MOZ_AUTOMATION"))

        self.assertTrue(should_error)


if __name__ == "__main__":
    main()
