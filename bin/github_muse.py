#!/usr/bin/env python3
"""GitHub REST API helper for the muse-chan bot account.

Generic by design: the `api` command can call any REST endpoint, so new
token scopes work without changing this helper. Convenience commands wrap
the common reads and writes.

Auth: the registered connection custom.github-muse-chan holds a classic
personal access token. dynamic_credentials places a surrogate in the
Authorization bearer header and Muse swaps in the real token only on an
approved request to api.github.com.
"""

import argparse
import json
import sys
import urllib.error
import urllib.parse
import urllib.request

sys.path.insert(0, "/opt/muse/skills/custom-connector-setup/bin")
from dynamic_credentials import add_surrogate_to_request, read_json_response

API_HOST = "api.github.com"
BASE = "https://" + API_HOST
PROVIDER = "custom.github-muse-chan"


class NoRedirect(urllib.request.HTTPRedirectHandler):
    def redirect_request(self, *args):
        raise RuntimeError("redirect refused, verify the endpoint")


def call(method, path, body=None, params=None):
    """Call the GitHub REST API and return (status, parsed_json_or_text)."""
    url = BASE + path
    if params:
        url += "?" + urllib.parse.urlencode(params)
    data = None
    headers = {
        "Accept": "application/vnd.github+json",
        "X-GitHub-Api-Version": "2022-11-28",
        "User-Agent": "muse-chan-connector",
    }
    if body is not None:
        data = json.dumps(body).encode("utf-8")
        headers["Content-Type"] = "application/json"
    request = urllib.request.Request(url, data=data, headers=headers, method=method)
    add_surrogate_to_request(request, PROVIDER, allowed_hosts=[API_HOST])
    opener = urllib.request.build_opener(NoRedirect())
    try:
        with opener.open(request, timeout=30) as response:
            return response.status, read_json_response(response)
    except urllib.error.HTTPError as err:
        try:
            payload = json.loads(err.read().decode("utf-8"))
        except Exception:
            payload = {"message": "unparseable error body"}
        return err.code, payload


def emit(status, payload):
    print(json.dumps({"status": status, "data": payload}, ensure_ascii=False, indent=2))
    return 0 if status < 400 else 1


def main():
    parser = argparse.ArgumentParser(description="GitHub API as muse-chan")
    sub = parser.add_subparsers(dest="command", required=True)

    sub.add_parser("me", help="GET /user, the authenticated bot account")

    p_api = sub.add_parser("api", help="call any REST endpoint")
    p_api.add_argument("method", choices=["GET", "POST", "PATCH", "PUT", "DELETE"])
    p_api.add_argument("path", help="path starting with /, for example /repos/otnc/some-repo")
    p_api.add_argument("--body", help="JSON request body as a string")

    p_repos = sub.add_parser("repos", help="list repositories of a user")
    p_repos.add_argument("username")

    p_repo = sub.add_parser("repo", help="show one repository")
    p_repo.add_argument("owner")
    p_repo.add_argument("name")

    p_issues = sub.add_parser("issues", help="list issues of a repository")
    p_issues.add_argument("owner")
    p_issues.add_argument("name")
    p_issues.add_argument("--state", default="open", choices=["open", "closed", "all"])

    p_pulls = sub.add_parser("pulls", help="list pull requests of a repository")
    p_pulls.add_argument("owner")
    p_pulls.add_argument("name")
    p_pulls.add_argument("--state", default="open", choices=["open", "closed", "all"])

    p_contents = sub.add_parser("contents", help="read a file or directory in a repository")
    p_contents.add_argument("owner")
    p_contents.add_argument("name")
    p_contents.add_argument("path", nargs="?", default="")
    p_contents.add_argument("--ref", default=None)

    args = parser.parse_args()

    if args.command == "me":
        status, payload = call("GET", "/user")
    elif args.command == "api":
        body = json.loads(args.body) if args.body else None
        status, payload = call(args.method, args.path, body=body)
    elif args.command == "repos":
        status, payload = call("GET", f"/users/{args.username}/repos",
                               params={"per_page": 100, "sort": "updated"})
    elif args.command == "repo":
        status, payload = call("GET", f"/repos/{args.owner}/{args.name}")
    elif args.command == "issues":
        status, payload = call("GET", f"/repos/{args.owner}/{args.name}/issues",
                               params={"state": args.state, "per_page": 100})
    elif args.command == "pulls":
        status, payload = call("GET", f"/repos/{args.owner}/{args.name}/pulls",
                               params={"state": args.state, "per_page": 100})
    elif args.command == "contents":
        params = {"ref": args.ref} if args.ref else None
        status, payload = call("GET", f"/repos/{args.owner}/{args.name}/contents/{args.path}",
                               params=params)
    else:  # pragma: no cover
        parser.error("unknown command")
    return emit(status, payload)


if __name__ == "__main__":
    sys.exit(main())
