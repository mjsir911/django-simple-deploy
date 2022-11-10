"""Unit tests for django-simple-deploy, targeting Heroku."""

from pathlib import Path
import subprocess

import pytest

import unit_tests.utils.ut_helper_functions as hf


# --- Fixtures ---

@pytest.fixture(scope='module')
def run_simple_deploy(reset_test_project, tmp_project):
    # Call simple_deploy here, so it can target this module's platform.
    sd_root_dir = Path(__file__).parents[3]
    cmd = f"sh utils/call_simple_deploy.sh -d {tmp_project} -p heroku -s {sd_root_dir}"
    cmd_parts = cmd.split()
    subprocess.run(cmd_parts)


# --- Test modifications to project files. ---

def test_settings(tmp_project, run_simple_deploy):
    """Verify settings have been changed for Platform.sh."""
    hf.check_reference_file(tmp_project, 'blog/settings.py', 'heroku')

def test_requirements_txt(tmp_project, run_simple_deploy):
    """Test that the requirements.txt file is correct."""
    hf.check_reference_file(tmp_project, 'requirements.txt', 'heroku')

def test_gitignore(tmp_project, run_simple_deploy):
    """Test that .gitignore has been modified correctly."""
    hf.check_reference_file(tmp_project, '.gitignore', 'heroku')


# --- Test Heroku-specific files ---

def test_generated_procfile(run_simple_deploy, tmp_project):
    """Test that the generated Procfile is correct."""
    hf.check_reference_file(tmp_project, 'Procfile', 'heroku')

def test_static_placeholder(run_simple_deploy, tmp_project):
    """Test that the static dir is present, with a placeholder.txt file."""
    hf.check_reference_file(tmp_project, 'static/placeholder.txt', 'heroku')


# --- Test logs ---

def test_log_dir(run_simple_deploy, tmp_project):
    """Test that the log directory exists, and contains an appropriate log file."""
    log_path = Path(tmp_project / 'simple_deploy_logs')
    assert log_path.exists()

    # There should be exactly two log files.
    log_files = sorted(log_path.glob('*'))
    log_filenames = [lf.name for lf in log_files]
    # Check for exactly the log files we expect to find.
    assert 'deployment_summary.html' in log_filenames
    # DEV: Add a regex text for a file like "simple_deploy_2022-07-09174245.log".
    assert len(log_files) == 2

    # Read log file.
    # DEV: Look for specific log file; not sure this log file is always the second one.
    #   We're looking for one similar to "simple_deploy_2022-07-09174245.log".
    log_file = log_files[1]
    log_file_text = log_file.read_text()

    # Spot check for opening log messages.
    assert "INFO: Logging run of `manage.py simple_deploy`..." in log_file_text
    assert "INFO: Configuring project for deployment to Heroku..." in log_file_text

    # Spot check for success messages.
    assert "INFO: --- Your project is now configured for deployment on Heroku. ---" in log_file_text
    assert "INFO: Or, you can visit https://sample-name-11894.herokuapp.com." in log_file_text


# --- Test staticfile setup ---

def test_one_static_file(run_simple_deploy, tmp_project):
    """There should be exactly one file in static/."""
    static_path = tmp_project / 'static'
    static_dir_files = sorted(static_path.glob('*'))
    assert len(static_dir_files) == 1


# # --- Test Heroku host already in ALLOWED_HOSTS ---
# DEV: Keeping this here for now; we probably want to update this test rather
#   than just get rid of it.

# def test_heroku_host_in_allowed_hosts(run_simple_deploy, tmp_project):
#     """Test that no ALLOWED_HOST entry in Heroku-specific settings if the
#     Heroku host is already in ALLOWED_HOSTS.
#     """
#     # Modify the test project, and rerun simple_deploy.
#     cmd = f'sh platforms/heroku/modify_allowed_hosts.sh -d {tmp_project}'
#     cmd_parts = cmd.split()
#     subprocess.run(cmd_parts)

#     # Check that there's no ALLOWED_HOSTS setting in the Heroku-specific settings.
#     #   If we use the settings_text fixture, we'll get the original settings text
#     #   because it has module-level scope.
#     settings_text = Path(tmp_project / 'blog/settings.py').read_text()
#     assert "    ALLOWED_HOSTS.append('sample-name-11894.herokuapp.com')" not in settings_text