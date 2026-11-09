# SolMarrow for Dify

Draft, schedule and track social media posts on 19 networks from Dify workflows and agents. SolMarrow has a free plan with unlimited posts.

Source: https://github.com/Shakil197/solmarrow-dify-plugin

## Setup and credentials

You need a SolMarrow API key (the credential).

1. In SolMarrow open **Settings → Apps and AI agents → API keys** and create a key (starts with `smk_`). One key reaches one workspace.
2. In Dify add the SolMarrow tool and paste the key.

## Usage

Use the tools in a workflow or agent:

| Tool | What it does |
| --- | --- |
| List workspaces | Workspaces the key can use |
| List accounts | Connected social accounts in a workspace |
| Create post | Save a draft or schedule a post (optional per-account text and options) |
| List posts | Posts by status and time range |
| Get post | One post with the result per account |
| Get analytics | Performance numbers for a workspace or post |
| Upload media from URL | Add an image or video from a public https link |

`workspace_id` is optional when the key reaches a single workspace. Times use ISO 8601 with an offset, like `2026-11-12T09:00:00+06:00`, at least 5 minutes ahead. Without a time, Create post saves a draft.

Privacy: see [PRIVACY.md](PRIVACY.md). Support: support@solmarrow.com
