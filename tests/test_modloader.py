import pytest
import sys
import os
from unittest.mock import MagicMock, patch, mock_open
import modloader

@pytest.fixture(autouse=True)
def reset_hooks():
    """Reset hooks and game state before each test."""
    modloader._hooks = {k: [] for k in modloader._hooks}
    modloader.game_state = {}
    yield

def test_update_game_state():
    modloader.update_game_state({'score': 100})
    assert modloader.game_state['score'] == 100
    modloader.update_game_state({'level': 2})
    assert modloader.game_state['score'] == 100
    assert modloader.game_state['level'] == 2

def test_get_game_state():
    modloader.game_state = {'test': 123}
    assert modloader.get_game_state() == {'test': 123}

def test_register_and_trigger_update():
    mock_func = MagicMock()
    modloader.register_on_update(mock_func)
    modloader.trigger_on_update(0.16)
    mock_func.assert_called_once_with(0.16)

def test_trigger_update_exception(capsys):
    def bad_func(delta):
        raise ValueError("Boom")
    
    modloader.register_on_update(bad_func)
    modloader.trigger_on_update(0.16)
    captured = capsys.readouterr()
    assert "Error in on_update hook: Boom" in captured.out

def test_register_and_trigger_draw_1_arg():
    mock_func = MagicMock()
    # Mock signature to look like func(screen)
    # modloader inspects signature, so we need a real function or correct mock
    def draw_func(screen):
        pass
    mock_draw = MagicMock(side_effect=draw_func)
    # MagicMock signature handling can be tricky, let's use a real wrapper or inspect patch
    # Easiest is to use the real function that calls the mock
    
    real_mock = MagicMock()
    def wrapper(screen):
        real_mock(screen)
        
    modloader.register_on_draw(wrapper)
    screen_mock = MagicMock()
    game_state_mock = MagicMock()
    
    modloader.trigger_on_draw(screen_mock, game_state_mock)
    real_mock.assert_called_once_with(screen_mock)

def test_register_and_trigger_draw_2_args(capsys):
    real_mock = MagicMock()
    def wrapper(screen, state):
        real_mock(screen, state)
        
    modloader.register_on_draw(wrapper)
    screen_mock = MagicMock()
    game_state_mock = MagicMock()
    
    modloader.trigger_on_draw(screen_mock, game_state_mock)
    real_mock.assert_called_once_with(screen_mock, game_state_mock)

def test_register_and_trigger_event():
    mock_func = MagicMock()
    modloader.register_on_event(mock_func)
    event_mock = MagicMock()
    modloader.trigger_on_event(event_mock)
    mock_func.assert_called_once_with(event_mock)

def test_register_and_trigger_collision_god_mode():
    # If any hook returns False, collision is cancelled
    modloader.register_on_collision(lambda: True)
    modloader.register_on_collision(lambda: False)
    modloader.register_on_collision(lambda: True)
    
    assert modloader.trigger_on_collision() is False

def test_register_and_trigger_collision_normal():
    modloader.register_on_collision(lambda: True)
    assert modloader.trigger_on_collision() is True

def test_trigger_collision_exception(capsys):
    def bad_hook():
        raise Exception("Ouch")
    modloader.register_on_collision(bad_hook)
    
    # Should default to True/Valid if error occurs? 
    # Logic: "collision_valid = True" ... try ... except: print
    # So yes, it returns True
    assert modloader.trigger_on_collision() is True
    captured = capsys.readouterr()
    assert "Error in on_collision hook: Ouch" in captured.out

def test_load_mods_no_mods(capsys):
    with patch('os.path.exists', return_value=True):
        with patch('os.listdir', return_value=[]):
            modloader.load_mods()
            captured = capsys.readouterr()
            assert "No mods found" in captured.out

def test_load_mods_success(capsys):
    # Mock two mods, one in local, one in user dir
    local_mod_content = "mod_api['register_on_jump'](lambda: print('JumpMod'))"
    
    with patch('os.makedirs'):
        with patch('os.path.exists', return_value=True):
            with patch('dependencies.get_user_data_dir', return_value="/tmp/user"):
                with patch('os.listdir') as mock_listdir:
                    # localized side effects for listdir
                    # First call (local), second call (user)
                    mock_listdir.side_effect = [
                        ['mod1.py', 'not_a_mod.txt'],
                        [] 
                    ]
                    
                    with patch('builtins.open', mock_open(read_data=local_mod_content)):
                         modloader.load_mods()
    
    # Check if loaded
    assert len(modloader._hooks['on_jump']) == 1
    captured = capsys.readouterr()
    assert "Loading 1 mod(s): mod1" in captured.out

def test_load_mods_execution_error(capsys):
    bad_mod = "raise ValueError('ModSyntaxError')"
    
    with patch('os.makedirs'), patch('os.path.exists', return_value=True), \
         patch('dependencies.get_user_data_dir', return_value="/tmp/user"), \
         patch('os.listdir', side_effect=[['bad.py'], []]), \
         patch('builtins.open', mock_open(read_data=bad_mod)):
        
        modloader.load_mods()
    
    captured = capsys.readouterr()
    assert "Error loading mod 'bad.py'" in captured.err
