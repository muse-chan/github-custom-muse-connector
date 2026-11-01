# GitHub (muse-chan)

- `custom.github-muse-chan` connects Muse to GitHub through the REST API. Every call acts as the bot account `muse-chan`, so commits, issues and pull requests show that account and its avatar.

- The connector authenticates with the registered `api_key` credential, a classic personal access token placed in the bearer header, and calls only `api.github.com`.

- The helper lives at `~/workspace/custom-connectors/custom.github-muse-chan/bin/github_muse.py`. It is generic on purpose, so a wider token scope later needs no helper change.

## Connect

- The connection was registered with `credentials.request_api_access` and these details. Reuse them to reconnect:

```json
{
  "provider": "github-muse-chan",
  "auth_scheme": "api_key",
  "placement": "bearer_header",
  "api_hosts": ["api.github.com"]
}
```

- Before the first change in a conversation, prove access with a harmless read:

```text
python3 ~/workspace/custom-connectors/custom.github-muse-chan/bin/github_muse.py me
```

- A healthy connection answers with status 200 and the `muse-chan` account. The commit author email for local git work as this account is `151584462+muse-chan@users.noreply.github.com`.

## Credentials

- The registered connection holds the credential. Helpers import `/opt/muse/skills/custom-connector-setup/bin/dynamic_credentials.py`, which returns an `hsurr:` surrogate and places it where the provider reads the key. Muse swaps in the real credential only on an approved request to a registered host.

- Never put a key, token, password or cookie in this doc, a helper, a command argument, an environment variable or a log. Never ask the user to paste one in chat.

- Keep redirects disabled on authenticated requests.

- On a 401 or 403, check the request first. Confirm that the helper attached the credential, that the host is registered and that the placement and scopes match.

- Only when a request that carried the credential is still rejected, call `credentials.request_api_access` with the details above and `"reconnect": true`.

## Call any endpoint

- Use the `api` command for any REST endpoint, reads and writes alike. Pass a JSON body with `--body` when the endpoint takes one.

```text
python3 ~/workspace/custom-connectors/custom.github-muse-chan/bin/github_muse.py api GET /repos/otnc/some-repo
python3 ~/workspace/custom-connectors/custom.github-muse-chan/bin/github_muse.py api POST /repos/otnc/some-repo/issues --body '{"title": "Bug report"}'
```

- The output is JSON with the HTTP `status` and the response `data`. Endpoints that paginate accept query parameters inside the path, for example `/repos/otnc/some-repo/commits?per_page=100`.

- Writes take effect as `muse-chan`. The token scope decides what succeeds, and a scope the token lacks answers 403 or 404.

## Convenience reads

- Show the authenticated account:

```text
python3 ~/workspace/custom-connectors/custom.github-muse-chan/bin/github_muse.py me
```

- List a user's repositories, show one repository, list its issues or pull requests, or read a path inside it:

```text
python3 ~/workspace/custom-connectors/custom.github-muse-chan/bin/github_muse.py repos muse-chan
python3 ~/workspace/custom-connectors/custom.github-muse-chan/bin/github_muse.py repo otnc some-repo
python3 ~/workspace/custom-connectors/custom.github-muse-chan/bin/github_muse.py issues otnc some-repo --state open
python3 ~/workspace/custom-connectors/custom.github-muse-chan/bin/github_muse.py pulls otnc some-repo --state open
python3 ~/workspace/custom-connectors/custom.github-muse-chan/bin/github_muse.py contents otnc some-repo README.md
```

- File contents come back base64 encoded in the `content` field. Decode before reading.

## Recover from errors

- A 401 means the credential was missing or rejected. Check the registration and placement before asking for a reconnect.

- A 403 with a rate limit message means the account hit the API rate limit. Stop and wait for the window named in the response instead of retrying.

- A 404 on a private repository usually means `muse-chan` has no access to it. The account must be a collaborator on the user's repositories before it can read or write them.

- After a failed or timed-out change, check the current state with a read before trying again, because the first request may have completed.

## Limits

- The token is a classic personal access token with the `repo` and `workflow` scopes. It cannot delete repositories, and repository rename or archive needs admin rights the account does not get as a write collaborator.

- Fine-grained tokens are not used here, because they cannot act on repositories where the account is only a repository collaborator.

- Operations that need scopes beyond `repo` and `workflow`, such as organization administration, fail until the token is regenerated with more scopes. The helper already covers them through the `api` command.

## Related skills

- Use `muse.skill_search` to find other skills and `muse.connector_search` to find other connectors.
