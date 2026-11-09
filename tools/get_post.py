from collections.abc import Generator
from typing import Any

from dify_plugin import Tool
from dify_plugin.entities.tool import ToolInvokeMessage

from solmarrow_client import SolMarrowError, UUID_RE, api_key_from, request


class GetPostTool(Tool):
    def _invoke(self, tool_parameters: dict[str, Any]) -> Generator[ToolInvokeMessage]:
        try:
            post_id = str(tool_parameters.get("post_id") or "").strip()
            if not UUID_RE.match(post_id):
                raise SolMarrowError("post_id must be an id from Create post or List posts.")
            data = request(api_key_from(self.runtime.credentials), "GET", f"/posts/{post_id}")
        except SolMarrowError as e:
            raise ValueError(str(e)) from e
        yield self.create_json_message(data)
