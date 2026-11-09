from collections.abc import Generator
from typing import Any

from dify_plugin import Tool
from dify_plugin.entities.tool import ToolInvokeMessage

from solmarrow_client import SolMarrowError, api_key_from, request, workspace_id


class ListAccountsTool(Tool):
    def _invoke(self, tool_parameters: dict[str, Any]) -> Generator[ToolInvokeMessage]:
        try:
            key = api_key_from(self.runtime.credentials)
            ws = workspace_id(key, tool_parameters.get("workspace_id"))
            data = request(key, "GET", f"/workspaces/{ws}/accounts")
        except SolMarrowError as e:
            raise ValueError(str(e)) from e
        yield self.create_json_message(data)
