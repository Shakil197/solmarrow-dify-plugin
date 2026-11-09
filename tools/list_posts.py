from collections.abc import Generator
from typing import Any

from dify_plugin import Tool
from dify_plugin.entities.tool import ToolInvokeMessage

from solmarrow_client import SolMarrowError, api_key_from, iso_time, request, workspace_id

STATUSES = {"draft", "scheduled", "publishing", "published", "partially_published", "failed"}


class ListPostsTool(Tool):
    def _invoke(self, tool_parameters: dict[str, Any]) -> Generator[ToolInvokeMessage]:
        try:
            key = api_key_from(self.runtime.credentials)
            ws = workspace_id(key, tool_parameters.get("workspace_id"))
            status = str(tool_parameters.get("status") or "").strip()
            if status and status not in STATUSES:
                raise SolMarrowError("status must be one of: " + ", ".join(sorted(STATUSES)))
            limit = tool_parameters.get("limit")
            params = {
                "status": status,
                "from": iso_time(tool_parameters.get("from"), "from"),
                "to": iso_time(tool_parameters.get("to"), "to"),
                "limit": max(1, min(50, int(limit))) if limit not in (None, "") else None,
            }
            data = request(key, "GET", f"/workspaces/{ws}/posts", params=params)
        except (SolMarrowError, ValueError) as e:
            raise ValueError(str(e)) from e
        yield self.create_json_message(data)
