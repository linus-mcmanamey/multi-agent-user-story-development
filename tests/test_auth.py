import json
import subprocess
from datetime import datetime, timedelta
from unittest.mock import Mock, patch

import pytest

from multi_agent_user_story_development.auth.azure import AzureLogin


class TestAzureLogin:
    """Test Azure authentication manager."""

    def test_azure_login_initialization(self):
        """Test that AzureLogin initializes with correct default values."""
        auth = AzureLogin()
        assert auth._last_check is None
        assert auth._last_check_result is False
        assert auth._check_interval == timedelta(minutes=5)


class TestCheckAzureLogin:
    """Test Azure CLI authentication checks."""

    def test_check_azure_login_success(self, mock_azure_auth: Mock):
        """Test successful Azure CLI authentication check."""
        mock_azure_auth.return_value.returncode = 0
        mock_azure_auth.return_value.stdout = '{"accessToken": "test_token"}'
        auth = AzureLogin()
        result = auth.check_azure_login()
        assert result is True
        assert mock_azure_auth.call_count >= 1

    def test_check_azure_login_not_authenticated(self):
        """Test Azure CLI check when not authenticated."""
        with patch("multi_agent_user_story_development.auth.azure.subprocess.run") as mock_run:
            mock_run.return_value.returncode = 1
            auth = AzureLogin()
            result = auth.check_azure_login()
            assert result is False

    def test_check_azure_login_token_expired(self):
        """Test Azure CLI check when token is expired."""
        with patch("multi_agent_user_story_development.auth.azure.subprocess.run") as mock_run:

            def side_effect(*args, **kwargs):
                if "account" in args[0] and "show" in args[0]:
                    return Mock(returncode=0)
                return Mock(returncode=1)

            mock_run.side_effect = side_effect
            auth = AzureLogin()
            result = auth.check_azure_login()
            assert result is False

    def test_check_azure_login_timeout(self):
        """Test Azure CLI check when subprocess times out."""
        with patch("multi_agent_user_story_development.auth.azure.subprocess.run") as mock_run:
            mock_run.side_effect = subprocess.TimeoutExpired("az", 10)
            auth = AzureLogin()
            result = auth.check_azure_login()
            assert result is False

    def test_check_azure_login_cli_not_found(self):
        """Test Azure CLI check when CLI is not installed."""
        with patch("multi_agent_user_story_development.auth.azure.subprocess.run") as mock_run:
            mock_run.side_effect = FileNotFoundError()
            auth = AzureLogin()
            result = auth.check_azure_login()
            assert result is False

    def test_check_azure_login_caches_result(self):
        """Test that Azure CLI check caches successful result."""
        with patch("multi_agent_user_story_development.auth.azure.subprocess.run") as mock_run:
            mock_run.return_value.returncode = 0
            mock_run.return_value.stdout = '{"accessToken": "test_token"}'
            auth = AzureLogin()
            result1 = auth.check_azure_login()
            result2 = auth.check_azure_login()
            assert result1 is True
            assert result2 is True
            assert mock_run.call_count == 2

    def test_check_azure_login_cache_expires(self):
        """Test that Azure CLI check cache expires after interval."""
        with patch("multi_agent_user_story_development.auth.azure.subprocess.run") as mock_run:
            mock_run.return_value.returncode = 0
            mock_run.return_value.stdout = '{"accessToken": "test_token"}'
            auth = AzureLogin()
            auth.check_azure_login()
            auth._last_check = datetime.now() - timedelta(minutes=6)
            auth.check_azure_login()
            assert mock_run.call_count >= 4


class TestCheckAzureDevOpsAuth:
    """Test Azure DevOps authentication checks."""

    def test_check_azure_devops_auth_success(self, mock_env_vars):
        """Test successful Azure DevOps authentication check."""
        with patch("multi_agent_user_story_development.auth.azure.subprocess.run") as mock_run:
            mock_run.return_value.returncode = 0
            mock_run.return_value.stdout = '{"value": [{"name": "Test Project"}]}'
            auth = AzureLogin()
            result = auth.check_azure_devops_auth()
            assert result is True

    def test_check_azure_devops_auth_missing_pat(self):
        """Test Azure DevOps check when PAT is missing."""
        with patch("multi_agent_user_story_development.auth.azure.os.getenv", return_value=None):
            auth = AzureLogin()
            result = auth.check_azure_devops_auth()
            assert result is False

    def test_check_azure_devops_auth_invalid_response(self, mock_env_vars):
        """Test Azure DevOps check with invalid JSON response."""
        with patch("multi_agent_user_story_development.auth.azure.subprocess.run") as mock_run:
            mock_run.return_value.returncode = 0
            mock_run.return_value.stdout = "Invalid JSON"
            auth = AzureLogin()
            result = auth.check_azure_devops_auth()
            assert result is False

    def test_check_azure_devops_auth_timeout(self, mock_env_vars):
        """Test Azure DevOps check when subprocess times out."""
        with patch("multi_agent_user_story_development.auth.azure.subprocess.run") as mock_run:
            mock_run.side_effect = subprocess.TimeoutExpired("az", 10)
            auth = AzureLogin()
            result = auth.check_azure_devops_auth()
            assert result is False

    def test_check_azure_devops_auth_custom_organization(self, mock_env_vars):
        """Test Azure DevOps check with custom organization."""
        with patch("multi_agent_user_story_development.auth.azure.subprocess.run") as mock_run:
            mock_run.return_value.returncode = 0
            mock_run.return_value.stdout = '{"value": [{"name": "Test Project"}]}'
            auth = AzureLogin()
            result = auth.check_azure_devops_auth(organization="https://dev.azure.com/custom_org")
            assert result is True
            assert "--organization" in mock_run.call_args[0][0]
            assert "https://dev.azure.com/custom_org" in mock_run.call_args[0][0]


class TestCheckFullAuthentication:
    """Test combined authentication checks."""

    def test_check_full_authentication_all_valid(self, mock_env_vars):
        """Test full authentication check when both CLI and DevOps are authenticated."""
        with patch.object(AzureLogin, "check_azure_login", return_value=True):
            with patch.object(AzureLogin, "check_azure_devops_auth", return_value=True):
                auth = AzureLogin()
                all_auth, status = auth.check_full_authentication()
                assert all_auth is True
                assert status["azure_cli"] is True
                assert status["azure_devops"] is True

    def test_check_full_authentication_cli_only(self, mock_env_vars):
        """Test full authentication check when only CLI is authenticated."""
        with patch.object(AzureLogin, "check_azure_login", return_value=True):
            with patch.object(AzureLogin, "check_azure_devops_auth", return_value=False):
                auth = AzureLogin()
                all_auth, status = auth.check_full_authentication()
                assert all_auth is False
                assert status["azure_cli"] is True
                assert status["azure_devops"] is False

    def test_check_full_authentication_none_valid(self):
        """Test full authentication check when neither CLI nor DevOps are authenticated."""
        with patch.object(AzureLogin, "check_azure_login", return_value=False):
            auth = AzureLogin()
            all_auth, status = auth.check_full_authentication()
            assert all_auth is False
            assert status["azure_cli"] is False
            assert status["azure_devops"] is False

    def test_check_full_authentication_skips_devops_when_cli_fails(self):
        """Test that DevOps check is skipped when CLI check fails."""
        with patch.object(AzureLogin, "check_azure_login", return_value=False):
            with patch.object(AzureLogin, "check_azure_devops_auth") as mock_devops:
                auth = AzureLogin()
                auth.check_full_authentication()
                mock_devops.assert_not_called()


class TestAzureLoginMethod:
    """Test Azure CLI login method."""

    def test_azure_login_already_authenticated(self):
        """Test login when already authenticated."""
        with patch.object(AzureLogin, "check_azure_login", return_value=True):
            auth = AzureLogin()
            result = auth.azure_login()
            assert result is True

    def test_azure_login_success(self, mock_env_vars):
        """Test successful Azure login."""
        with patch.object(AzureLogin, "check_azure_login", return_value=False):
            with patch("multi_agent_user_story_development.auth.azure.subprocess.run") as mock_run:
                mock_run.return_value.returncode = 0
                auth = AzureLogin()
                result = auth.azure_login()
                assert result is True
                assert mock_run.called

    def test_azure_login_with_devops(self, mock_env_vars):
        """Test Azure login with DevOps configuration."""
        with patch.object(AzureLogin, "check_azure_login", return_value=False):
            with patch.object(AzureLogin, "check_azure_devops_auth", return_value=False):
                with patch("multi_agent_user_story_development.auth.azure.subprocess.run") as mock_run:
                    mock_run.return_value.returncode = 0
                    auth = AzureLogin()
                    result = auth.azure_login(include_devops=True)
                    assert result is True

    def test_azure_login_devops_missing_pat(self):
        """Test Azure login with DevOps when PAT is missing."""
        with patch.object(AzureLogin, "check_azure_login", return_value=False):
            with patch.object(AzureLogin, "check_azure_devops_auth", return_value=False):
                with patch("multi_agent_user_story_development.auth.azure.subprocess.run") as mock_run:
                    mock_run.return_value.returncode = 0
                    with patch("multi_agent_user_story_development.auth.azure.os.getenv", return_value=None):
                        auth = AzureLogin()
                        result = auth.azure_login(include_devops=True)
                        assert result is False

    def test_azure_login_timeout(self):
        """Test Azure login timeout handling."""
        with patch.object(AzureLogin, "check_azure_login", return_value=False):
            with patch("multi_agent_user_story_development.auth.azure.subprocess.run") as mock_run:
                mock_run.side_effect = subprocess.TimeoutExpired("az", 300)
                auth = AzureLogin()
                result = auth.azure_login()
                assert result is False

    def test_azure_login_keyboard_interrupt(self):
        """Test Azure login keyboard interrupt handling."""
        with patch.object(AzureLogin, "check_azure_login", return_value=False):
            with patch("multi_agent_user_story_development.auth.azure.subprocess.run") as mock_run:
                mock_run.side_effect = KeyboardInterrupt()
                auth = AzureLogin()
                result = auth.azure_login()
                assert result is False

    def test_azure_login_failure(self):
        """Test Azure login failure handling."""
        with patch.object(AzureLogin, "check_azure_login", return_value=False):
            with patch("multi_agent_user_story_development.auth.azure.subprocess.run") as mock_run:
                mock_run.return_value.returncode = 1
                auth = AzureLogin()
                result = auth.azure_login()
                assert result is False


class TestForceRelogin:
    """Test force relogin functionality."""

    def test_force_relogin_success(self, mock_env_vars):
        """Test successful forced relogin."""
        with patch("multi_agent_user_story_development.auth.azure.subprocess.run") as mock_run:
            mock_run.return_value.returncode = 0
            with patch.object(AzureLogin, "azure_login", return_value=True) as mock_login:
                auth = AzureLogin()
                result = auth.force_relogin()
                assert result is True
                assert mock_login.called
                assert mock_run.call_count >= 2

    def test_force_relogin_includes_devops_by_default(self, mock_env_vars):
        """Test that force relogin includes DevOps configuration by default."""
        with patch("multi_agent_user_story_development.auth.azure.subprocess.run") as mock_run:
            mock_run.return_value.returncode = 0
            with patch.object(AzureLogin, "azure_login", return_value=True) as mock_login:
                auth = AzureLogin()
                auth.force_relogin()
                mock_login.assert_called_once()
                assert mock_login.call_args[1]["include_devops"] is True

    def test_force_relogin_custom_organization(self, mock_env_vars):
        """Test force relogin with custom organization."""
        with patch("multi_agent_user_story_development.auth.azure.subprocess.run") as mock_run:
            mock_run.return_value.returncode = 0
            with patch.object(AzureLogin, "azure_login", return_value=True) as mock_login:
                auth = AzureLogin()
                auth.force_relogin(organization="https://dev.azure.com/custom_org")
                assert mock_login.call_args[1]["organization"] == "https://dev.azure.com/custom_org"

    def test_force_relogin_error_handling(self):
        """Test force relogin error handling."""
        with patch("multi_agent_user_story_development.auth.azure.subprocess.run") as mock_run:
            mock_run.side_effect = Exception("Test error")
            auth = AzureLogin()
            result = auth.force_relogin()
            assert result is False
