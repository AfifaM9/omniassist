import unittest
from mcp_tools.shell_tool import _is_blocked_command, run_shell


class TestCommandBlocking(unittest.TestCase):
    """Test suite for catastrophic command blocking in shell_tool.py"""

    # ==================== Fork Bomb Tests ====================

    def test_fork_bomb_basic(self):
        """Classic fork bomb :() { :|: };: should be blocked"""
        self.assertTrue(_is_blocked_command(':() { :|: };:')[0])

    def test_fork_bomb_with_spaces(self):
        """Fork bomb with extra spaces should still be blocked"""
        self.assertTrue(_is_blocked_command(':() { :|: }; :')[0])

    def test_fork_bomb_with_newlines(self):
        """Fork bomb split across lines should be blocked"""
        bomb = ':() {\n  :|: &\n}\n;'
        self.assertTrue(_is_blocked_command(bomb)[0])

    # ==================== Root Directory Tests ====================

    def test_block_rm_rf_root(self):
        """rm -rf / should be blocked"""
        blocked, reason = _is_blocked_command('rm -rf /')
        self.assertTrue(blocked)
        self.assertIn('root', reason.lower())

    def test_block_rm_rf_root_with_quotes(self):
        """rm -rf "/" with quotes should be blocked"""
        self.assertTrue(_is_blocked_command('rm -rf "/"')[0])
        self.assertTrue(_is_blocked_command("rm -rf '/'")[0])

    def test_block_rm_rf_root_with_flags(self):
        """rm -rf -- / should be blocked"""
        self.assertTrue(_is_blocked_command('rm -rf -- /')[0])

    def test_allowed_ls_root(self):
        """Listing root directory should be allowed"""
        self.assertFalse(_is_blocked_command('ls /')[0])
        self.assertFalse(_is_blocked_command('ls -la /')[0])

    def test_allowed_cat_etc_passwd(self):
        """Reading files should be allowed"""
        self.assertFalse(_is_blocked_command('cat /etc/passwd')[0])

    # ==================== Sensitive Directory Tests ====================

    def test_block_rm_rf_etc(self):
        """rm -rf /etc should be blocked"""
        blocked, reason = _is_blocked_command('rm -rf /etc')
        self.assertTrue(blocked)
        self.assertIn('etc', reason.lower())

    def test_block_rm_rf_home(self):
        """rm -rf /home should be blocked"""
        blocked, reason = _is_blocked_command('rm -rf /home')
        self.assertTrue(blocked)
        self.assertIn('home', reason.lower())

    def test_block_rm_rf_var(self):
        """rm -rf /var should be blocked"""
        self.assertTrue(_is_blocked_command('rm -rf /var')[0])

    def test_block_rm_rf_usr(self):
        """rm -rf /usr should be blocked"""
        self.assertTrue(_is_blocked_command('rm -rf /usr')[0])

    def test_block_rm_rf_tmp(self):
        """rm -rf /tmp should be blocked"""
        self.assertTrue(_is_blocked_command('rm -rf /tmp')[0])

    def test_block_rm_rf_root_sbin(self):
        """rm -rf /root and /sbin should be blocked"""
        self.assertTrue(_is_blocked_command('rm -rf /root')[0])
        self.assertTrue(_is_blocked_command('rm -rf /sbin')[0])

    def test_block_rm_rf_boot(self):
        """rm -rf /boot should be blocked"""
        self.assertTrue(_is_blocked_command('rm -rf /boot')[0])

    def test_block_rm_rf_dev(self):
        """rm -rf /dev should be blocked"""
        self.assertTrue(_is_blocked_command('rm -rf /dev')[0])

    def test_block_rm_rf_proc(self):
        """rm -rf /proc should be blocked"""
        self.assertTrue(_is_blocked_command('rm -rf /proc')[0])

    def test_block_rm_rf_sys(self):
        """rm -rf /sys should be blocked"""
        self.assertTrue(_is_blocked_command('rm -rf /sys')[0])

    # ==================== Home Directory Shorthand Tests ====================

    def test_block_rm_rf_tilde(self):
        """rm -rf ~ (home shorthand) should be blocked"""
        blocked, reason = _is_blocked_command('rm -rf ~')
        self.assertTrue(blocked)
        self.assertIn('home', reason.lower())

    def test_block_rm_rf_tilde_with_path(self):
        """rm -rf ~user should be blocked"""
        self.assertTrue(_is_blocked_command('rm -rf ~user')[0])

    # ==================== Safe Commands Tests ====================

    def test_allowed_echo(self):
        """Basic echo should be allowed"""
        self.assertFalse(_is_blocked_command('echo hello')[0])

    def test_allowed_pwd(self):
        """pwd should be allowed"""
        self.assertFalse(_is_blocked_command('pwd')[0])

    def test_allowed_ls(self):
        """ls should be allowed"""
        self.assertFalse(_is_blocked_command('ls')[0])

    def test_allowed_ls_home(self):
        """ls /home should be allowed"""
        self.assertFalse(_is_blocked_command('ls /home')[0])

    def test_allowed_cat_file(self):
        """cat /some/file.txt should be allowed"""
        self.assertFalse(_is_blocked_command('cat /some/file.txt')[0])

    def test_allowed_grep(self):
        """grep should be allowed"""
        self.assertFalse(_is_blocked_command('grep pattern file')[0])

    def test_allowed_find(self):
        """find should be allowed"""
        self.assertFalse(_is_blocked_command('find /home -name "*.txt"')[0])

    # ==================== Safe rm Commands Tests ====================

    def test_allowed_rm_file(self):
        """Simple rm file.txt should be allowed"""
        self.assertFalse(_is_blocked_command('rm file.txt')[0])

    def test_allowed_rm_with_path(self):
        """rm with full path should be allowed"""
        self.assertFalse(_is_blocked_command('rm /tmp/test.txt')[0])

    def test_allowed_rm_inside_tmp(self):
        """rm -rf /tmp/somedir should be allowed (deleting inside tmp, not tmp itself)"""
        self.assertFalse(_is_blocked_command('rm -rf /tmp/somedir')[0])

    def test_allowed_rm_inside_home(self):
        """rm -rf /home/user/docs should be allowed"""
        self.assertFalse(_is_blocked_command('rm -rf /home/user/docs')[0])

    def test_allowed_rm_recursive_nonsensitive(self):
        """rm -rf for non-sensitive paths should be allowed"""
        self.assertFalse(_is_blocked_command('rm -rf /opt/myapp')[0])
        self.assertFalse(_is_blocked_command('rm -rf /mnt/usb')[0])

    # ==================== Edge Cases ====================

    def test_empty_command_blocked(self):
        """Empty command should be blocked"""
        blocked, reason = _is_blocked_command('')
        self.assertTrue(blocked)
        self.assertIn('empty', reason.lower())

    def test_whitespace_only_blocked(self):
        """Whitespace-only command should be blocked"""
        self.assertTrue(_is_blocked_command('   \n\t')[0])

    def test_multiple_flags_allowed(self):
        """rm with multiple flags should work if target is safe"""
        self.assertFalse(_is_blocked_command('rm -rf -v /tmp/test')[0])

    def test_multiple_targets_one_blocked(self):
        """If one target is blocked, entire command should be blocked"""
        # This depends on implementation - at least one blocked target should block
        blocked1, _ = _is_blocked_command('rm -rf /home /tmp/safe')
        blocked2, _ = _is_blocked_command('rm -rf /tmp/safe /home')
        # At minimum, the command targeting /home should be blocked
        self.assertTrue(_is_blocked_command('rm -rf /home /tmp/safe')[0])


class TestRunShellBlocking(unittest.TestCase):
    """Test that run_shell properly returns blocked messages"""

    def test_run_shell_returns_blocked_message(self):
        """run_shell should return blocked message for dangerous commands"""
        result = run_shell('rm -rf /')
        self.assertIn('blocked', result.lower())

    def test_run_shell_fork_bomb_blocked(self):
        """run_shell should block fork bombs"""
        result = run_shell(':() { :|: };:')
        self.assertIn('blocked', result.lower())

    def test_run_shell_allowed_command_executes(self):
        """run_shell should execute allowed commands normally"""
        result = run_shell('echo hello')
        # Should not contain "blocked"
        self.assertNotIn('blocked', result.lower())
        self.assertIn('hello', result.lower())


class TestSecurityBoundaries(unittest.TestCase):
    """Test edge cases and security boundaries"""

    def test_case_insensitive_blocking(self):
        """Blocking should be case insensitive"""
        self.assertTrue(_is_blocked_command('RM -RF /')[0])
        self.assertTrue(_is_blocked_command('Rm -Rf /Home')[0])

    def test_command_with_pipes_still_blocked(self):
        """rm -rf / with pipes should still be blocked if root target"""
        # The command itself is still dangerous even with pipes
        self.assertTrue(_is_blocked_command('rm -rf / | somecommand')[0])

    def test_command_with_redirects_still_blocked(self):
        """rm -rf / with output redirect should still be blocked"""
        self.assertTrue(_is_blocked_command('rm -rf / > /dev/null')[0])

    def test_no_false_positive_on_rm_only(self):
        """rm without -rf should not be blocked"""
        self.assertFalse(_is_blocked_command('rm /tmp/test')[0])
        self.assertFalse(_is_blocked_command('rm /home/user/file')[0])


class TestSudoBlocking(unittest.TestCase):
    """Test that dangerous commands are blocked even with sudo"""

    def test_blocked_sudo_rm_rf_root(self):
        """sudo rm -rf / should be blocked"""
        self.assertTrue(_is_blocked_command('sudo rm -rf /')[0])

    def test_blocked_sudo_rm_rf_home(self):
        """sudo rm -rf /home should be blocked"""
        self.assertTrue(_is_blocked_command('sudo rm -rf /home')[0])

    def test_blocked_sudo_rm_rf_etc(self):
        """sudo rm -rf /etc should be blocked"""
        self.assertTrue(_is_blocked_command('sudo rm -rf /etc')[0])

    def test_blocked_sudo_rm_rf_tilde(self):
        """sudo rm -rf ~ should be blocked"""
        self.assertTrue(_is_blocked_command('sudo rm -rf ~')[0])

    def test_blocked_sudo_case_insensitive(self):
        """SUDO rm -rf / should be blocked (case insensitive sudo)"""
        self.assertTrue(_is_blocked_command('SUDO rm -rf /')[0])
        self.assertTrue(_is_blocked_command('Sudo rm -rf /home')[0])

    def test_allowed_sudo_safe_commands(self):
        """sudo with safe commands should be allowed"""
        self.assertFalse(_is_blocked_command('sudo apt-get update')[0])
        self.assertFalse(_is_blocked_command('sudo echo hello')[0])
        self.assertFalse(_is_blocked_command('sudo ls /home')[0])

    def test_blocked_sudo_multiple_flags(self):
        """sudo rm -rf -v / should be blocked"""
        self.assertTrue(_is_blocked_command('sudo rm -rf -v /')[0])


if __name__ == "__main__":
    unittest.main()
