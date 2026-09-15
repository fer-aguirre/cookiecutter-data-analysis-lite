import pytest
from unittest.mock import mock_open
from hooks.post_gen_project import (
    setup_poetry, setup_uv, setup_git, main, run_command, remove_quarto_files,
    update_pyproject_file, Colors
)
import subprocess

class TestPostGenProject:

    def test_setup_poetry_success(self, mocker):
        mocker.patch('hooks.post_gen_project.run_command', return_value=True)

        assert setup_poetry() is True

    def test_setup_uv_success(self, mocker):
        mocker.patch('hooks.post_gen_project.run_command', return_value=True)

        assert setup_uv() is True

    def test_setup_git_success(self, mocker):
        mocker.patch('hooks.post_gen_project.run_command', return_value=True)
        
        assert setup_git() is True

    def test_unsupported_package_manager_error(self, mocker):
        mocker.patch('hooks.post_gen_project.PACKAGE_MANAGER', 'unsupported')
        mocker.patch('hooks.post_gen_project.print_status')
        
        assert main() == 1

    def test_poetry_installation_failure(self, mocker):
        mocker.patch('hooks.post_gen_project.run_command', side_effect=[False])
        mock_open_instance = mock_open()
        mocker.patch('builtins.open', mock_open_instance)
        
        assert setup_poetry() is False

    def test_git_initialization_failure(self, mocker):
        mocker.patch('hooks.post_gen_project.run_command', side_effect=[True, True, False])
        
        assert setup_git() is False

    def test_update_pyproject_file_poetry_success(self, mocker):
        mocker.patch('hooks.post_gen_project.PACKAGE_MANAGER', 'poetry')
        mocker.patch('hooks.post_gen_project.PYTHON_VERSION', '3.11')
        mocker.patch('os.path.exists', return_value=True)
        mock_open_instance = mock_open(read_data='python = "^3.8"')
        mocker.patch('builtins.open', mock_open_instance)

        update_pyproject_file()

        mock_open_instance.assert_any_call("pyproject.toml", "r", encoding="utf-8")
        mock_open_instance.assert_any_call("pyproject.toml", "w", encoding="utf-8")
        written_content = "".join(
            call.args[0] for call in mock_open_instance().write.call_args_list
        )
        assert 'python = "^3.11"' in written_content

    def test_update_pyproject_file_missing_file_is_noop(self, mocker):
        mocker.patch('os.path.exists', return_value=False)
        mock_open_instance = mock_open()
        mocker.patch('builtins.open', mock_open_instance)

        update_pyproject_file()

        mock_open_instance.assert_not_called()

    def test_uv_virtualenv_creation_failure(self, mocker):
        mocker.patch('hooks.post_gen_project.run_command', side_effect=[True, False])
        mock_open_instance = mock_open()
        mocker.patch('builtins.open', mock_open_instance)

        assert setup_uv() is False

    def test_remove_quarto_files_when_not_included(self, mocker):
        mocker.patch('hooks.post_gen_project.INCLUDE_QUARTO', 'No')
        mocker.patch('hooks.post_gen_project.QUARTO_PATHS', ['_quarto.yml', 'custom.scss', 'index.qmd', 'docs'])
        mocker.patch('os.path.isdir', side_effect=lambda p: p == 'docs')
        mocker.patch('os.path.exists', return_value=True)
        mock_rmtree = mocker.patch('shutil.rmtree')
        mock_remove = mocker.patch('os.remove')

        remove_quarto_files()

        mock_rmtree.assert_called_once_with('docs')
        assert mock_remove.call_count == 3
        mock_remove.assert_any_call('_quarto.yml')
        mock_remove.assert_any_call('custom.scss')
        mock_remove.assert_any_call('index.qmd')

    def test_remove_quarto_files_when_included(self, mocker):
        mocker.patch('hooks.post_gen_project.INCLUDE_QUARTO', 'Yes')
        mock_rmtree = mocker.patch('shutil.rmtree')
        mock_remove = mocker.patch('os.remove')

        remove_quarto_files()

        mock_rmtree.assert_not_called()
        mock_remove.assert_not_called()
