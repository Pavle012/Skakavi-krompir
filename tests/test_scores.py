import pytest
from unittest.mock import patch, MagicMock
import requests
import scores

@patch('requests.post')
def test_submit_score_success(mock_post):
    mock_post.return_value.status_code = 200
    mock_post.return_value.json.return_value = {"status": "success"}
    
    scores.submit_score("Player1", 100)
    
    mock_post.assert_called_once()
    args, kwargs = mock_post.call_args
    assert kwargs['json']['player'] == "Player1"
    assert kwargs['json']['score'] == 100
    assert kwargs['json']['secret'] == scores.SECRET_KEY

@patch('requests.get')
def test_get_leaderboard_success(mock_get):
    mock_get.return_value.status_code = 200
    mock_get.return_value.json.return_value = [{"player": "Player1", "score": 100}]
    
    lb = scores.get_leaderboard(limit=5)
    
    assert lb == [{"player": "Player1", "score": 100}]
    mock_get.assert_called_once()
    assert mock_get.call_args[1]['params']['limit'] == 5

@patch('requests.get', side_effect=requests.exceptions.RequestException)
def test_get_leaderboard_failure(mock_get):
    lb = scores.get_leaderboard()
    assert lb is None
