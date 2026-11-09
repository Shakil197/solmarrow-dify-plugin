from collections.abc import Generator
from typing import Any

from dify_plugin import Tool
from dify_plugin.entities.tool import ToolInvokeMessage

from solmarrow_client import SolMarrowError, api_key_from, id_list, iso_time, json_object, request, workspace_id


class CreatePostTool(Tool):
    def _invoke(self, tool_parameters: dict[str, Any]) -> Generator[ToolInvokeMessage]:
        try:
            key = api_key_from(self.runtime.credentials)
            ws = workspace_id(key, tool_parameters.get("workspace_id"))
            body: dict[str, Any] = {"text": str(tool_parameters.get("text") or "")}
            accounts = id_list(tool_parameters.get("account_ids"), "account_ids", 50)
            media = id_list(tool_parameters.get("media_ids"), "media_ids", 35)
            if accounts:
                body["account_ids"] = accounts
            if media:
                body["media_ids"] = media
            when = iso_time(tool_parameters.get("schedule_at"), "schedule_at")
            if when:
                body["schedule_at"] = when
            elif tool_parameters.get("publish_now") is True:
                body["publish_now"] = True
            else:
                body["draft"] = True
            for name in ("per_account_text", "per_account_options"):
                value = json_object(tool_parameters.get(name), name)
                if value:
                    body[name] = value
            if not body["text"].strip() and not media:
                raise SolMarrowError("Add post text or at least one media id.")
            if not body.get("draft") and not accounts:
                raise SolMarrowError("Choose at least one account_id to schedule or publish a post.")
            headers = {}
            idem = str(tool_parameters.get("idempotency_key") or "").strip()
            if idem:
                headers["Idempotency-Key"] = idem[:200]
            data = request(key, "POST", f"/workspaces/{ws}/posts", body=body, headers=headers)
        except SolMarrowError as e:
            raise ValueError(str(e)) from e
        yield self.create_json_message(data)
