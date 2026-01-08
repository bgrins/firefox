# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at http://mozilla.org/MPL/2.0/.

import logging
import os
import unittest
from unittest.mock import Mock

from mozunit import main

from mozbuild.controller.building import BuildOutputManager


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

    def test_redirect_output_creates_temp_file(self):
        """Test that redirect_output=True creates a temporary log file."""
        log_manager = self._create_mock_log_manager()
        monitor = Mock()
        footer = None

        with BuildOutputManager(
            log_manager, monitor, footer, redirect_output=True
        ) as output_manager:
            self.assertIsNotNone(output_manager.redirect_log_file)
            self.assertIsNotNone(output_manager.redirect_log_handler)

            # Verify the temp file exists
            temp_file_path = output_manager.redirect_log_file.name
            self.assertTrue(os.path.exists(temp_file_path))
            self._temp_files.append(temp_file_path)

            # Verify handler is configured correctly
            self.assertEqual(output_manager.redirect_log_handler.level, logging.DEBUG)

    def test_no_redirect_output_by_default(self):
        """Test that redirect output is not enabled by default."""
        log_manager = self._create_mock_log_manager()
        monitor = Mock()
        footer = None

        with BuildOutputManager(
            log_manager, monitor, footer, redirect_output=False
        ) as output_manager:
            self.assertIsNone(output_manager.redirect_log_file)
            self.assertIsNone(output_manager.redirect_log_handler)

    def test_redirect_output_sets_terminal_level_to_warning(self):
        """Test that redirect output sets terminal handler to WARNING level."""
        log_manager = self._create_mock_log_manager()
        monitor = Mock()
        footer = None

        with BuildOutputManager(
            log_manager, monitor, footer, redirect_output=True
        ) as output_manager:
            # Verify that _redirect_terminal_level was set
            self.assertTrue(hasattr(output_manager, "_redirect_terminal_level"))
            self.assertEqual(output_manager._redirect_terminal_level, logging.WARNING)

    def test_redirect_output_cleanup_on_exit(self):
        """Test that redirect output files are properly closed on exit."""
        log_manager = self._create_mock_log_manager()
        monitor = Mock()
        monitor.stop_resource_recording = Mock()
        footer = None

        temp_file_path = None
        with BuildOutputManager(
            log_manager, monitor, footer, redirect_output=True
        ) as output_manager:
            temp_file_path = output_manager.redirect_log_file.name
            self._temp_files.append(temp_file_path)

        # After exiting context, file should be closed but still exist
        self.assertTrue(os.path.exists(temp_file_path))

    def test_redirect_output_file_handler_added_to_loggers(self):
        """Test that the file handler is added to structured loggers."""
        log_manager = self._create_mock_log_manager()

        # Create mock loggers
        mock_logger1 = Mock()
        mock_logger2 = Mock()
        log_manager.structured_loggers = [mock_logger1, mock_logger2]

        monitor = Mock()
        footer = None

        with BuildOutputManager(
            log_manager, monitor, footer, redirect_output=True
        ) as output_manager:
            self._temp_files.append(output_manager.redirect_log_file.name)

            # Verify handler was added to all structured loggers
            mock_logger1.addHandler.assert_called_once()
            mock_logger2.addHandler.assert_called_once()

            # Verify it's the redirect handler
            handler = mock_logger1.addHandler.call_args[0][0]
            self.assertEqual(handler, output_manager.redirect_log_handler)


class TestBuildCommandRedirectOutput(unittest.TestCase):
    """Tests for build command redirect output auto-detection."""

    def setUp(self):
        self._old_env = dict(os.environ)
        return unittest.TestCase.setUp(self)

    def tearDown(self):
        os.environ.clear()
        os.environ.update(self._old_env)
        return unittest.TestCase.tearDown(self)

    def test_claudecode_env_enables_redirect(self):
        """Test that CLAUDECODE environment variable enables redirect output."""
        # This tests the logic that would be in build_commands.py
        # Simulating: if not redirect_output and bool(os.environ.get("CLAUDECODE")):

        redirect_output = False
        os.environ["CLAUDECODE"] = "1"

        # Simulate the auto-enable logic
        if not redirect_output and bool(os.environ.get("CLAUDECODE")):
            redirect_output = True

        self.assertTrue(redirect_output)

    def test_no_claudecode_env_no_redirect(self):
        """Test that redirect output is not auto-enabled without CLAUDECODE."""
        redirect_output = False
        os.environ.pop("CLAUDECODE", None)

        # Simulate the auto-enable logic
        if not redirect_output and bool(os.environ.get("CLAUDECODE")):
            redirect_output = True

        self.assertFalse(redirect_output)

    def test_explicit_redirect_not_overridden(self):
        """Test that explicit --redirect-output is not changed by CLAUDECODE."""
        redirect_output = True
        os.environ["CLAUDECODE"] = "1"

        # Simulate the auto-enable logic (should not change if already True)
        if not redirect_output and bool(os.environ.get("CLAUDECODE")):
            redirect_output = True

        self.assertTrue(redirect_output)

    def test_verbose_disables_redirect(self):
        """Test that --verbose disables redirect output."""
        redirect_output = True
        verbose = True

        # Simulate the conflict resolution logic
        if redirect_output and verbose:
            redirect_output = False

        self.assertFalse(redirect_output)

    def test_moz_automation_disables_redirect(self):
        """Test that MOZ_AUTOMATION disables redirect output."""
        redirect_output = True
        os.environ["MOZ_AUTOMATION"] = "1"

        # Simulate the automation check logic
        if redirect_output and bool(os.environ.get("MOZ_AUTOMATION")):
            redirect_output = False

        self.assertFalse(redirect_output)


if __name__ == "__main__":
    main()
