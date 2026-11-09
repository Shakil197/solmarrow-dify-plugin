from collections.abc import Generator
from typing import Any

from dify_plugin import Tool
from dify_plugin.entities.tool import ToolInvokeMessage

from solmarrow_client import SolMarrowError, UUID_RE, api_key_from, iso_time, request, workspace_id


class GetAnalyticsTool(Tool):
    def _invoke(self, tool_parameters: dict[str, Any]) -> Generator[ToolInvokeMessage]:
        try:
            key = api_key_from(self.runtime.credentials)
            ws = workspace_id(key, tool_parameters.get("workspace_id"))
            post_id = str(tool_parameters.get("post_id") or "").strip()
            if post_id and not UUID_RE.match(post_id):
                raise SolMarrowError("post_id must be an id from List posts.")
            params = {
                "from": iso_time(tool_parameters.get("from"), "from"),
                "to": iso_time(tool_parameters.get("to"), "to"),
                "post_id": post_id,
            }
            data = request(key, "GET", f"/workspaces/{ws}/analytics", params=params)
        except SolMarrowError as e:
            raise ValueError(str(e)) from e
        yield self.create_json_message(data)
