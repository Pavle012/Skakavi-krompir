import pytest
import sys
import os
import platform
import subprocess
from unittest.mock import MagicMock, patch
import updater

def test_start_update_unsupported_os(capsys):
    with patch('platform.system', return_value='Darwin'): # MacOS
        updater.start_update("game.exe")
        captured = capsys.readouterr()
        assert "Updater not supported for OS: Darwin" in captured.err

def test_start_update_linux():
    with patch('platform.system', return_value='Linux'):
        with patch('urllib.request.urlretrieve') as mock_download:
            with patch('subprocess.Popen') as mock_popen:
                with patch('os.chmod') as mock_chmod:
                    with patch('tempfile.gettempdir', return_value='/tmp'):
                        updater.start_update("/app/game")
                        
                        expected_url = "https://raw.githubusercontent.com/Pavle012/Skakavi-krompir/main/updater.sh"
                        expected_script = "/tmp/updater.sh"
                        
                        mock_download.assert_called_once_with(expected_url, expected_script)
                        mock_chmod.assert_called_once_with(expected_script, 0o755)
                        
                        cmd = mock_popen.call_args[0][0]
                        assert cmd == ['bash', expected_script, '/app/game']

def test_start_update_windows():
    with patch('platform.system', return_value='Windows'):
        with patch('urllib.request.urlretrieve') as mock_download:
            with patch('subprocess.Popen') as mock_popen:
                with patch('tempfile.gettempdir', return_value='C:\\Temp'):
                    with patch('os.chmod'): # Prevent FileNotFoundError on Linux
                        # Windows paths in arguments can be tricky in tests on Linux,
                        # but the logic just passes strings.
                        updater.start_update("C:\\Game\\game.exe")
                        
                        expected_url = "https://raw.githubusercontent.com/Pavle012/Skakavi-krompir/main/updater.bat"
                        # On Linux, os.path.join will result in mixed separators "C:\Temp/updater.bat"
                        # We should match what os.path.join actually produces in the test environment
                        expected_script = os.path.join("C:\\Temp", "updater.bat")
                        
                        mock_download.assert_called_once_with(expected_url, expected_script)
                        
                        cmd = mock_popen.call_args[0][0]
                        # On Windows, it passed [] + [script, game_path]
                        assert cmd == [expected_script, os.path.abspath("C:\\Game\\game.exe")]

def test_start_update_exception(capsys):
    with patch('platform.system', return_value='Linux'):
        with patch('urllib.request.urlretrieve', side_effect=Exception("Network Down")):
             updater.start_update("game")
             captured = capsys.readouterr()
             assert "An error occurred during the update process: Network Down" in captured.err
