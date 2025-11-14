import os
import subprocess
from datetime import datetime, timedelta
from typing import Dict, Optional, Tuple

from dotenv import load_dotenv
from loguru import logger

load_dotenv()


class AzureLogin:
    """Azure authentication manager for CLI and DevOps access."""

    def __init__(self) -> None:
        self._last_check: Optional[datetime] = None
        self._last_check_result: bool = False
        self._check_interval = timedelta(minutes=5)

    def check_azure_login(self) -> bool:
        """Check if Azure CLI is authenticated and token is still valid."""
        if self._last_check and datetime.now() - self._last_check < self._check_interval:
            logger.debug(f"Using cached auth status: {self._last_check_result}")
            return self._last_check_result
        try:
            result = subprocess.run(["az", "account", "show"], capture_output=True, text=True, timeout=10)
            if result.returncode == 0:
                token_result = subprocess.run(["az", "account", "get-access-token", "--resource", "https://management.azure.com/"], capture_output=True, text=True, timeout=10)
                if token_result.returncode == 0:
                    logger.debug("Azure CLI authentication is valid")
                    self._last_check = datetime.now()
                    self._last_check_result = True
                    return True
                else:
                    logger.debug("Azure CLI token appears to be expired")
                    self._last_check = datetime.now()
                    self._last_check_result = False
                    return False
            self._last_check = datetime.now()
            self._last_check_result = False
            return False
        except (subprocess.TimeoutExpired, FileNotFoundError):
            self._last_check = datetime.now()
            self._last_check_result = False
            return False
        except Exception as e:
            logger.debug(f"Error checking Azure login: {e}")
            self._last_check = datetime.now()
            self._last_check_result = False
            return False

    def check_azure_devops_auth(self, organization: str = "https://dev.azure.com/emstas") -> bool:
        """Check if Azure DevOps is authenticated by attempting to list projects using PAT."""
        try:
            pat = os.getenv("AZURE_DEVOPS_PAT")
            if not pat:
                logger.error("AZURE_DEVOPS_PAT not found in environment variables")
                return False
            env = os.environ.copy()
            env["AZURE_DEVOPS_EXT_PAT"] = pat
            result = subprocess.run(["az", "devops", "project", "list", "--organization", organization, "--top", "1", "--output", "json"], capture_output=True, text=True, timeout=10, env=env)
            if result.returncode == 0:
                try:
                    import json
                    data = json.loads(result.stdout)
                    return "value" in data and isinstance(data["value"], list)
                except (json.JSONDecodeError, KeyError):
                    return False
            return False
        except (subprocess.TimeoutExpired, FileNotFoundError):
            return False
        except Exception as e:
            logger.debug(f"Azure DevOps auth check failed: {e}")
            return False

    def check_full_authentication(self, organization: str = "https://dev.azure.com/emstas") -> Tuple[bool, Dict[str, bool]]:
        """Check both Azure CLI and Azure DevOps authentication status."""
        status = {"azure_cli": False, "azure_devops": False}
        status["azure_cli"] = self.check_azure_login()
        if status["azure_cli"]:
            status["azure_devops"] = self.check_azure_devops_auth(organization)
        all_authenticated = all(status.values())
        return all_authenticated, status

    def azure_login(self, include_devops: bool = False, organization: str = "https://dev.azure.com/emstas") -> bool:
        """Perform Azure CLI login and optionally configure Azure DevOps."""
        if self.check_azure_login():
            logger.info("Azure CLI already authenticated, skipping login.")
            return True
        logger.info("Azure CLI authentication required. Starting browser-based login...")
        logger.info("This will open a web browser for Azure authentication.")
        try:
            result = subprocess.run(["az", "login", "--allow-no-subscriptions", "--use-device-code"], timeout=300)
            if result.returncode == 0:
                logger.success("Azure CLI authentication successful!")
                if include_devops:
                    if not self.check_azure_devops_auth(organization):
                        logger.info("Setting up Azure DevOps authentication...")
                        pat = os.getenv("AZURE_DEVOPS_PAT")
                        if pat:
                            env = os.environ.copy()
                            env["AZURE_DEVOPS_EXT_PAT"] = pat
                            try:
                                subprocess.run(["az", "devops", "configure", "--defaults", f"organization={organization}"], capture_output=True, env=env, timeout=10)
                                logger.success("Azure DevOps configuration completed!")
                            except subprocess.TimeoutExpired:
                                logger.warning("Azure DevOps configuration timed out, but may still be configured.")
                            except Exception as e:
                                logger.warning(f"Azure DevOps configuration warning: {e}")
                        else:
                            logger.error("AZURE_DEVOPS_PAT not found in environment variables.")
                            logger.info("Please add AZURE_DEVOPS_PAT to your .env file.")
                            return False
                    else:
                        logger.success("Azure DevOps already authenticated!")
                return True
            else:
                logger.error("Azure authentication failed.")
                return False
        except subprocess.TimeoutExpired:
            logger.error("Authentication timeout (5 minutes). Please try again.")
            return False
        except KeyboardInterrupt:
            logger.warning("\nAuthentication cancelled by user.")
            return False
        except Exception as e:
            logger.error(f"Authentication error: {e}")
            return False

    def force_relogin(self, include_devops: bool = True, organization: str = "https://dev.azure.com/emstas") -> bool:
        """Force a fresh login to both Azure CLI and Azure DevOps."""
        logger.info("Forcing fresh Azure authentication...")
        try:
            subprocess.run(["az", "logout"], capture_output=True, timeout=10)
            subprocess.run(["az", "devops", "configure", "--defaults", "organization="], capture_output=True, timeout=10)
            return self.azure_login(include_devops, organization)
        except Exception as e:
            logger.error(f"Error during forced re-login: {e}")
            return False
