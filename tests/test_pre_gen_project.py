import pytest
from unittest.mock import patch
from hooks.pre_gen_project import validate_project_slug, print_colored, main, ERROR_COLOR, MESSAGE_COLOR, RESET_ALL

class TestPreGenProject:

    def test_validate_project_slug_valid(self):
        assert validate_project_slug("valid_slug") is None

    def test_print_colored_default_color(self, capsys):
        print_colored("Test message")
        captured = capsys.readouterr()
        assert captured.out == f"{MESSAGE_COLOR}Test message{RESET_ALL}\n"

    @patch('os.getcwd', return_value='/mocked/path')
    def test_main_exit_code_success(self, mock_getcwd):
        with patch('hooks.pre_gen_project.PROJECT_SLUG', 'valid_slug'):
            assert main() == 0

    def test_validate_project_slug_invalid_characters(self):
        error_message = validate_project_slug("invalid-slug")
        assert error_message is not None
        assert "ERROR: The project slug 'invalid-slug' is not a valid Python module name." in error_message

    def test_print_colored_error_message(self, capsys):
        print_colored("Error message", ERROR_COLOR)
        captured = capsys.readouterr()
        assert captured.out == f"{ERROR_COLOR}Error message{RESET_ALL}\n"

    @patch('os.getcwd', return_value='/mocked/path')
    def test_main_exit_code_failure(self, mock_getcwd):
        with patch('hooks.pre_gen_project.PROJECT_SLUG', 'invalid-slug'):
            assert main() == 1