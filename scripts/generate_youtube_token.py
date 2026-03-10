import argparse
import os
import sys
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials

# Must match the scopes in the youtube-mcp server's auth.ts
SCOPES = [
    "https://www.googleapis.com/auth/youtube",
    "https://www.googleapis.com/auth/youtube.force-ssl",
    "https://www.googleapis.com/auth/youtube.upload",
]

CREDS_BASE = os.path.join(
    os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "credentials"
)


def refresh_token(creds_dir: str) -> None:
    """Run the OAuth flow for a single credentials directory."""
    credentials_file = os.path.join(creds_dir, "credentials.json")
    token_file = os.path.join(creds_dir, "token.json")

    if not os.path.exists(credentials_file):
        print(f"Error: {credentials_file} not found", file=sys.stderr)
        sys.exit(1)

    creds = None
    if os.path.exists(token_file):
        creds = Credentials.from_authorized_user_file(token_file, SCOPES)

    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            print(f"Refreshing expired token in {creds_dir}...")
            creds.refresh(Request())
        else:
            print(f"Starting OAuth flow for {creds_dir}...")
            print("A browser window will open — sign in and approve access.")
            flow = InstalledAppFlow.from_client_secrets_file(
                credentials_file, SCOPES
            )
            creds = flow.run_local_server(port=0)
        with open(token_file, "w") as f:
            f.write(creds.to_json())

    print(f"Token ready: {token_file}")


def main():
    parser = argparse.ArgumentParser(
        description="Generate or refresh YouTube OAuth tokens for the MCP server"
    )
    parser.add_argument(
        "account",
        choices=["personal", "work", "both"],
        help="Which account to refresh",
    )
    args = parser.parse_args()

    accounts = ["personal", "work"] if args.account == "both" else [args.account]
    for account in accounts:
        refresh_token(os.path.join(CREDS_BASE, account))


if __name__ == "__main__":
    main()
