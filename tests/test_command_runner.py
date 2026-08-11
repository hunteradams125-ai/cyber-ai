import logging
import unittest

from core.command_runner import CommandRunner


class CommandRunnerTests(unittest.TestCase):
    def test_empty_command_is_rejected(self) -> None:
        runner = CommandRunner(logging.getLogger("test-command-runner"))
        with self.assertRaises(ValueError):
            runner.run([])

    def test_missing_optional_tool_is_nonfatal(self) -> None:
        runner = CommandRunner(logging.getLogger("test-command-runner"))
        result = runner.run(["command-that-does-not-exist-cyber-ai"])
        self.assertTrue(result.unavailable)
        self.assertFalse(result.ok)

    def test_known_safe_command_uses_argument_array(self) -> None:
        runner = CommandRunner(logging.getLogger("test-command-runner"))
        result = runner.run(["python", "-c", "print('fixture')"])
        self.assertTrue(result.ok)
        self.assertEqual(result.stdout.strip(), "fixture")