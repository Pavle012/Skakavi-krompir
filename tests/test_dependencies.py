import os
import sys
import pytest
from unittest.mock import patch, MagicMock
import dependencies

def test_is_compiled(monkeypatch):
    # Test non-compiled
    monkeypatch.setattr(sys, 'frozen', False, raising=False)
    if "__compiled__" in dependencies.__dict__:
        monkeypatch.delitem(dependencies.__dict__, "__compiled__")
    assert dependencies.is_compiled() is False

    # Test frozen
    monkeypatch.setattr(sys, 'frozen', True, raising=False)
    assert dependencies.is_compiled() is True

    # Test Nuitka
    monkeypatch.setattr(sys, 'frozen', False, raising=False)
    monkeypatch.setitem(dependencies.__dict__, "__compiled__", True)
    assert dependencies.is_compiled() is True

def test_get_user_data_dir_linux(monkeypatch):
    monkeypatch.setattr(sys, 'platform', 'linux')
    with patch('os.path.expanduser', return_value='/home/user'):
        with patch('os.makedirs'):
            with patch('os.path.exists', return_value=True):
                data_dir = dependencies.get_user_data_dir()
                assert data_dir == '/home/user/.local/share/SkakaviKrompir'

def test_get_user_data_dir_windows(monkeypatch):
    monkeypatch.setattr(sys, 'platform', 'win32')
    monkeypatch.setenv('APPDATA', 'C:\\Users\\user\\AppData\\Roaming')
    with patch('os.makedirs'):
        with patch('os.path.exists', return_value=True):
            data_dir = dependencies.get_user_data_dir()
            # Use os.path.join to match the test runner's OS behavior
            expected = os.path.join('C:\\Users\\user\\AppData\\Roaming', 'SkakaviKrompir')
            assert data_dir == expected

def test_resource_path_dev(monkeypatch):
    monkeypatch.setattr(sys, 'platform', 'linux')
    monkeypatch.delattr(sys, '_MEIPASS', raising=False)
    with patch('dependencies.is_compiled', return_value=False):
        path = dependencies.resource_path('assets/potato.png')
        assert os.path.basename(path) == 'potato.png'
        assert os.path.isabs(path)

@patch('dependencies.get_user_data_dir', return_value='/tmp/data')
@patch('os.path.exists', side_effect=lambda x: x == '/tmp/data/potato.png')
def test_get_potato_path_custom(mock_exists, mock_get_user_data):
    path = dependencies.get_potato_path()
    assert path == '/tmp/data/potato.png'

@patch('dependencies.get_user_data_dir', return_value='/tmp/data')
@patch('os.path.exists', return_value=False)
@patch('dependencies.resource_path', return_value='/app/assets/potato.png')
def test_get_potato_path_default(mock_res_path, mock_exists, mock_get_user_data):
    path = dependencies.get_potato_path()
    assert path == '/app/assets/potato.png'
