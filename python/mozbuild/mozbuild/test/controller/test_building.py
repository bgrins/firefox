# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at http://mozilla.org/MPL/2.0/.

import logging
import os
import shutil
import tempfile
import unittest
from unittest.mock import Mock

from mozunit import main

from mozbuild.controller.building import BuildOutputManager


class TestBuildOutputManager(unittest.TestCase):
    """Tests for BuildOutputManager show functionality."""

    def setUp(self):
        self.test_objdir = tempfile.mkdtemp()
        return unittest.TestCase.setUp(self)

    def tearDown(self):
        shutil.rmtree(self.test_objdir, ignore_errors=True)
        return unittest.TestCase.tearDown(self)

    def test_show_warning_creates_log_file(self):
        """Test that show='warning' creates a log file and sets up handlers."""
        log_manager = Mock()
        log_manager.terminal = Mock()
        log_manager.terminal_formatter = Mock()
        log_manager.structured_loggers = []
        log_manager.terminal_handler = Mock()
        log_manager.replace_terminal_handler = Mock(
            return_value=Mock(level=logging.INFO)
        )

        monitor = Mock()
        monitor.topobjdir = self.test_objdir
        monitor.stop_resource_recording = Mock()
        footer = None

        with BuildOutputManager(
            log_manager, monitor, footer, show="warning"
        ) as output_manager:
            # Verify log file was created
            expected_path = os.path.join(monitor.topobjdir, "last_build.txt")
            self.assertTrue(os.path.exists(expected_path))
            self.assertIsNotNone(output_manager.redirect_log_file)
            self.assertIsNotNone(output_manager.redirect_log_handler)

            # Verify handler is set to capture all output
            self.assertEqual(output_manager.redirect_log_handler.level, logging.DEBUG)

            # Verify terminal handler was set to WARNING level
            log_manager.terminal_handler.setLevel.assert_called_with(logging.WARNING)


if __name__ == "__main__":
    main()
