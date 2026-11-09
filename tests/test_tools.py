import sys
from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

import solmarrow_client as c  # noqa: E402
from tools.create_post import CreatePostTool  # noqa: E402
from tools.list_posts import ListPostsTool  # noqa: E402
from tools.get_post import GetPostTool  # noqa: E402
from tools.upload_media_from_url import UploadMediaFromUrlTool  # noqa: E402
from tools.list_workspaces import ListWorkspacesTool  # noqa: E402

WS = "11111111-1111-4111-8111-111111111111"
ACC = "22222222-2222-4222-8222-222222222222"
KEY = "smk_test"


def resp(data, status=200):
    r = MagicMock()
    r.status_code = status
    r.ok = status < 400
    r.json.return_value = data
    return r


def run(tool_cls, params):
    tool = tool_cls.from_credentials({"api_key": KEY})
    return [m.message.json_object if hasattr(m.message, "json_object") else m for m in tool.invoke(params)]


def test_workspace_id_single_is_picked():
    with patch("requests.request", return_value=resp({"workspaces": [{"id": WS}]})):
        assert c.workspace_id(KEY, "") == WS


def test_workspace_id_many_needs_choice():
    with patch("requests.request", return_value=resp({"workspaces": [{"id": WS}, {"id": ACC}]})):
        with pytest.raises(c.SolMarrowError):
            c.workspace_id(KEY, "")


def test_401_message():
    with patch("requests.request", return_value=resp({"error": {"status": 401, "message": "x"}}, 401)):
        with pytest.raises(c.SolMarrowError, match="API key"):
            c.request(KEY, "GET", "/workspaces")


def test_error_body_message_passes_through():
    with patch("requests.request", return_value=resp({"error": {"status": 400, "message": "Pick a time at least 5 minutes ahead."}}, 400)):
        with pytest.raises(c.SolMarrowError, match="5 minutes"):
            c.request(KEY, "POST", "/x", body={})


def test_create_post_draft_default():
    with patch("requests.request", return_value=resp({"post": {"id": WS}})) as req:
        run(CreatePostTool, {"workspace_id": WS, "text": "hi"})
    body = req.call_args.kwargs["json"]
    assert body == {"text": "hi", "draft": True}
    assert req.call_args.args[1].endswith(f"/workspaces/{WS}/posts")


def test_create_post_schedule_needs_accounts_and_offset():
    with pytest.raises(ValueError, match="time zone"):
        run(CreatePostTool, {"workspace_id": WS, "text": "hi", "account_ids": ACC, "schedule_at": "2026-11-12T09:00:00"})
    with patch("requests.request", return_value=resp({"post": {}})) as req:
        run(CreatePostTool, {"workspace_id": WS, "text": "hi", "account_ids": f"{ACC}, {ACC}", "schedule_at": "2026-11-12T09:00:00+06:00", "per_account_text": f'{{"{ACC}": "x"}}', "idempotency_key": "k1"})
    kw = req.call_args.kwargs
    assert kw["json"]["account_ids"] == [ACC]
    assert kw["json"]["per_account_text"] == {ACC: "x"}
    assert kw["headers"]["Idempotency-Key"] == "k1"


def test_create_post_publish_without_account_fails():
    with pytest.raises(ValueError, match="account"):
        run(CreatePostTool, {"workspace_id": WS, "text": "hi", "publish_now": True})


def test_list_posts_params():
    with patch("requests.request", return_value=resp({"posts": []})) as req:
        run(ListPostsTool, {"workspace_id": WS, "status": "scheduled", "limit": 500})
    assert req.call_args.kwargs["params"] == {"status": "scheduled", "limit": 50}


def test_list_posts_bad_status():
    with pytest.raises(ValueError):
        run(ListPostsTool, {"workspace_id": WS, "status": "nope"})


def test_get_post_validates_id():
    with pytest.raises(ValueError):
        run(GetPostTool, {"post_id": "../x"})


def test_upload_requires_https():
    with pytest.raises(ValueError, match="https"):
        run(UploadMediaFromUrlTool, {"workspace_id": WS, "url": "http://a/b.png"})


def test_list_workspaces_ok():
    with patch("requests.request", return_value=resp({"workspaces": []})):
        out = run(ListWorkspacesTool, {})
    assert out
