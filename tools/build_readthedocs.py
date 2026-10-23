"""Trigger an authenticated Read the Docs build; never print the API token."""
import argparse
import json
import os
from pathlib import Path
import urllib.error
import urllib.request


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--token-file", type=Path, help="Private token file outside the repository")
    args = parser.parse_args()
    token = args.token_file.read_text().strip() if args.token_file else os.environ.get("READTHEDOCS_TOKEN", "").strip()
    if not token:
        parser.error("Provide --token-file or set READTHEDOCS_TOKEN")
    request = urllib.request.Request(
        "https://app.readthedocs.org/api/v3/projects/time-reshape/versions/latest/builds/",
        data=b"{}", method="POST",
        headers={"Authorization": "Token " + token, "Content-Type": "application/json"},
    )
    try:
        with urllib.request.urlopen(request, timeout=30) as response:
            result = json.load(response)
    except urllib.error.HTTPError as error:
        raise SystemExit(f"Read the Docs rejected the request (HTTP {error.code}); check access in the project dashboard.") from None
    except urllib.error.URLError:
        raise SystemExit("Could not reach Read the Docs. Check the build list before retrying to avoid duplicate builds.") from None
    if not result.get("triggered"):
        raise SystemExit("Build was not triggered; check the project dashboard.")
    print(result["build"]["urls"]["build"])
    print("Build requested. Open this link to confirm success and the Git commit.")


if __name__ == "__main__":
    main()
