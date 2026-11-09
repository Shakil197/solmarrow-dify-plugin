from collections.abc import Generator
from typing import Any
from urllib.parse import urlparse

from dify_plugin import Tool
from dify_plugin.entities.tool import ToolInvokeMessage

from solmarrow_client import SolMarrowError, api_key_from, request, workspace_id


class UploadMediaFromUrlTool(Tool):
    def _invoke(self, tool_parameters: dict[str, Any]) -> Generator[ToolInvokeMessage]:
        try:
            key = api_key_from(self.runtime.credentials)
            ws = workspace_id(key, tool_parameters.get("workspace_id"))
            url = str(tool_parameters.get("url") or "").strip()
            if urlparse(url).scheme != "https":
                raise SolMarrowError("url must be a public https link to an image or video.")
            body: dict[str, Any] = {"url": url}
            name = str(tool_parameters.get("file_name") or "").strip()
            if name:
                body["file_name"] = name
            data = request(key, "POST", f"/workspaces/{ws}/media/from-url", body=body)
        except SolMarrowError as e:
            raise ValueError(str(e)) from e
        yield self.create_json_message(data)
