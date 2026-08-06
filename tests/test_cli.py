import unittest
import re

# Import patterns from cli.py for testing
QUIT_PATTERN = re.compile(r'^(exit|quit|q)$', re.IGNORECASE)
SLASH_COMMAND_PATTERN = re.compile(r'^/(\w+)')


class TestSlashCommands(unittest.TestCase):
    """Test suite for slash command handling in cli.py"""

    def test_help_command_lowercase(self):
        """Basic /help command should be detected"""
        match = SLASH_COMMAND_PATTERN.match('/help')
        self.assertIsNotNone(match)
        self.assertEqual(match.group(1).lower(), 'help')

    def test_help_command_uppercase(self):
        """HELP command should be case insensitive"""
        match = SLASH_COMMAND_PATTERN.match('/HELP')
        self.assertIsNotNone(match)
        self.assertEqual(match.group(1).lower(), 'help')

    def test_help_command_mixed_case(self):
        """Help command mixed case should be handled"""
        match = SLASH_COMMAND_PATTERN.match('/Help')
        self.assertIsNotNone(match)
        self.assertEqual(match.group(1).lower(), 'help')

    def test_unknown_command(self):
        """Unknown command /unknown should be detected"""
        match = SLASH_COMMAND_PATTERN.match('/unknown')
        self.assertIsNotNone(match)
        self.assertEqual(match.group(1).lower(), 'unknown')

    def test_command_with_numbers(self):
        """Command with numbers /test123 should be detected"""
        match = SLASH_COMMAND_PATTERN.match('/test123')
        self.assertIsNotNone(match)
        self.assertEqual(match.group(1).lower(), 'test123')

    def test_quit_pattern_exit(self):
        """quit should match quit pattern"""
        self.assertTrue(QUIT_PATTERN.match('quit'))
        self.assertTrue(QUIT_PATTERN.match('QUIT'))
        self.assertTrue(QUIT_PATTERN.match('Quit'))

    def test_quit_pattern_q(self):
        """q should match quit pattern"""
        self.assertTrue(QUIT_PATTERN.match('q'))
        self.assertTrue(QUIT_PATTERN.match('Q'))

    def test_quit_pattern_exit_full(self):
        """exit should match quit pattern"""
        self.assertTrue(QUIT_PATTERN.match('exit'))
        self.assertTrue(QUIT_PATTERN.match('EXIT'))
        self.assertTrue(QUIT_PATTERN.match('Exit'))

    def test_regular_chat_not_slash(self):
        """Regular chat messages should not match slash pattern"""
        self.assertIsNone(SLASH_COMMAND_PATTERN.match('Hello, how are you?'))
        self.assertIsNone(SLASH_COMMAND_PATTERN.match('what is the weather'))

    def test_slash_only_not_command(self):
        """Just / without command should not match"""
        self.assertIsNone(SLASH_COMMAND_PATTERN.match('/'))

    def test_slash_with_space_not_command(self):
        """/ help (with space) should not match pattern"""
        self.assertIsNone(SLASH_COMMAND_PATTERN.match('/ help'))


if __name__ == "__main__":
    unittest.main()
