"""CLI argument and relaunch tests for ``picker_lib.cli``."""

import sys
import unittest
from unittest import mock

from picker_lib import cli


class TestParseArgs(unittest.TestCase):
    def test_defaults(self):
        args = cli.parse_args([])
        self.assertIsNone(args.preview)
        self.assertIsNone(args.backend)
        self.assertIsNone(args.db_path)

    def test_parses_all_options(self):
        args = cli.parse_args(
            ["--preview", "7", "--backend", "cliphist", "--db-path", "/tmp/db"]
        )
        self.assertEqual(args.preview, "7")
        self.assertEqual(args.backend, "cliphist")
        self.assertEqual(args.db_path, "/tmp/db")


class TestRelaunchCommand(unittest.TestCase):
    def test_uses_the_entry_point(self):
        with mock.patch.object(sys, "argv", ["/opt/bin/clipboard"]):
            self.assertEqual(
                cli.relaunch_command(), [sys.executable, "/opt/bin/clipboard"]
            )


class TestPreviewMode(unittest.TestCase):
    def test_rejects_a_non_numeric_id(self):
        self.assertEqual(cli.preview_mode("abc", None, None), 2)
