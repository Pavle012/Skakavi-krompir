# Testing Guide

This project uses `pytest` for unit testing. The tests are located in the `tests/` directory.

## How to Run Tests Locally

1. Ensure you have the development dependencies installed:
   ```bash
   pip install -r requirements-dev.txt
   ```
2. Run the tests:
   ```bash
   PYTHONPATH=. pytest
   ```

## How to Create a New Test

1. **Create a new file**: Add a file in the `tests/` directory with the prefix `test_`, e.g., `tests/test_new_feature.py`.
2. **Import modules**: Import the module you want to test and any necessary testing tools.
   ```python
   import pytest
   from unittest.mock import patch
   import my_module
   ```
3. **Write a test function**: Create a function prefixed with `test_`.
   ```python
   def test_my_feature():
       result = my_module.do_something()
       assert result == "expected_value"
   ```
4. **Mocking**: Use `unittest.mock.patch` to isolate the code being tested from external dependencies like files or network requests.
   ```python
   @patch('os.path.exists', return_value=True)
   def test_with_mock(mock_exists):
       assert my_module.check_file("foo.txt") is True
   ```
5. **Monkeypatching**: Use the `monkeypatch` fixture to modify attributes of modules (like `sys.platform`) safely.
   ```python
   def test_platform_logic(monkeypatch):
       monkeypatch.setattr(sys, 'platform', 'win32')
       # test code...
   ```

## Continuous Integration

Tests are automatically run on every push and pull request via GitHub Actions. You can view the status in the **Actions** tab of the repository.
