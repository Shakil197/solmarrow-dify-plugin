from collections.abc import Generator
from typing import Any

from dify_plugin import Tool
from dify_plugin.entities.tool import ToolInvokeMessage

from solmarrow_client import SolMarrowError, api_key_from, request


class ListWorkspacesTool(Tool):
    def _invoke(self, tool_parameters: dict[str, Any]) -> Generator[ToolInvokeMessage]:
        try:
            data = request(api_key_from(self.runtime.credentials), "GET", "/workspaces")
        except SolMarrowError as e:
            raise ValueError(str(e)) from e
        yield self.create_json_message(data)
