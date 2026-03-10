"""
YouTube API Authentication Module.
Handles OAuth2 flow for YouTube Data API v3 and YouTube Analytics API.
"""

import os
import json
import logging
from pathlib import Path
from typing import Optional, List

from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build

logger = logging.getLogger(__name__)

# Scopes required for YouTube Data API + Analytics API
SCOPES = [
    'https://www.googleapis.com/auth/youtube.readonly',
    'https://www.googleapis.com/auth/yt-analytics.readonly',
]

# Default paths
CREDENTIALS_ROOT = Path(__file__).parent.parent.parent / 'credentials'
DEFAULT_ACCOUNT = 'work'
DEFAULT_CREDENTIALS_PATH = CREDENTIALS_ROOT / DEFAULT_ACCOUNT / 'credentials.json'
DEFAULT_TOKEN_PATH = CREDENTIALS_ROOT / DEFAULT_ACCOUNT / 'token-analytics.json'


def get_credentials(
    credentials_path: Optional[Path] = None,
    token_path: Optional[Path] = None,
    scopes: Optional[List[str]] = None
) -> Credentials:
    """
    Get valid OAuth2 credentials, refreshing or initiating flow as needed.

    Args:
        credentials_path: Path to OAuth client credentials JSON (from Google Cloud Console)
        token_path: Path to store/load the user's access token
        scopes: List of OAuth scopes to request

    Returns:
        Valid Credentials object
    """
    if credentials_path and isinstance(credentials_path, str):
        credentials_path = Path(credentials_path)
    if token_path and isinstance(token_path, str):
        token_path = Path(token_path)

    credentials_path = credentials_path or DEFAULT_CREDENTIALS_PATH
    token_path = token_path or DEFAULT_TOKEN_PATH
    scopes = scopes or SCOPES

    creds = None

    # Load existing token if available
    if token_path.exists():
        try:
            creds = Credentials.from_authorized_user_file(str(token_path), scopes)
            logger.debug(f"Loaded existing credentials from {token_path}")
        except Exception as e:
            logger.warning(f"Failed to load existing token: {e}")

    # Refresh or obtain new credentials
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            logger.info("Refreshing expired credentials...")
            creds.refresh(Request())
        else:
            if not credentials_path.exists():
                raise FileNotFoundError(
                    f"OAuth credentials not found at {credentials_path}. "
                    "Download from Google Cloud Console and save there."
                )

            logger.info("Starting OAuth flow...")
            flow = InstalledAppFlow.from_client_secrets_file(
                str(credentials_path), scopes
            )
            creds = flow.run_local_server(port=0)

        # Save credentials for next run
        token_path.parent.mkdir(parents=True, exist_ok=True)
        with open(token_path, 'w') as token_file:
            token_file.write(creds.to_json())
        logger.info(f"Saved credentials to {token_path}")

    return creds


def get_authenticated_service(
    api_name: str = 'youtube',
    api_version: str = 'v3',
    credentials_path: Optional[Path] = None,
    token_path: Optional[Path] = None
):
    """
    Build an authenticated API service.

    Args:
        api_name: API to authenticate ('youtube' or 'youtubeAnalytics')
        api_version: API version
        credentials_path: Path to OAuth credentials
        token_path: Path to token storage

    Returns:
        Authenticated API service object
    """
    creds = get_credentials(credentials_path, token_path)
    service = build(api_name, api_version, credentials=creds)
    logger.info(f"Built authenticated {api_name} {api_version} service")
    return service


def setup_oauth(credentials_path: Optional[str] = None) -> bool:
    """
    Interactive setup for OAuth credentials.

    Args:
        credentials_path: Path to the credentials.json file

    Returns:
        True if setup successful
    """
    creds_path = Path(credentials_path) if credentials_path else DEFAULT_CREDENTIALS_PATH

    print("=" * 60)
    print("YouTube API OAuth Setup")
    print("=" * 60)

    if not creds_path.exists():
        print(f"\nCredentials file not found at: {creds_path}")
        print("\nTo set up YouTube API access:")
        print("1. Go to https://console.cloud.google.com/")
        print("2. Create a new project (or select existing)")
        print("3. Enable 'YouTube Data API v3' and 'YouTube Analytics API'")
        print("4. Go to Credentials > Create Credentials > OAuth Client ID")
        print("5. Select 'Desktop application'")
        print("6. Download the JSON and save as:")
        print(f"   {creds_path}")
        return False

    print(f"\nFound credentials at: {creds_path}")
    print("Starting OAuth flow (browser will open)...")

    try:
        creds = get_credentials(creds_path)
        print("\nAuthentication successful!")
        print(f"Token saved to: {DEFAULT_TOKEN_PATH}")
        return True
    except Exception as e:
        print(f"\nAuthentication failed: {e}")
        return False


if __name__ == '__main__':
    # Run interactive setup when executed directly
    logging.basicConfig(level=logging.INFO)
    setup_oauth()
