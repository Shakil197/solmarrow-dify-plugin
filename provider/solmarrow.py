from typing import Any

from dify_plugin import ToolProvider
from dify_plugin.errors.tool import ToolProviderCredentialValidationError

from solmarrow_client import SolMarrowError, api_key_from, request


class SolMarrowProvider(ToolProvider):
    def _validate_credentials(self, credentials: dict[str, Any]) -> None:
        try:
            request(api_key_from(credentials), "GET", "/workspaces")
        except SolMarrowError as e:
            raise ToolProviderCredentialValidationError(str(e)) from e
