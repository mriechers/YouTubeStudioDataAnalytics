# YouTube MCP - Personal/Work Account Separation

This server is configured to run as **two separate Docker containers** with distinct Google accounts to maintain clear separation between personal and work YouTube channels.

## Architecture

```
youtube-mcp/
├── src/                        # Server source code
├── credentials/
│   ├── personal/               # Personal Google account credentials
│   │   ├── credentials.json    # OAuth client config (from Google Cloud Console)
│   │   └── token.json          # Auth token (generated during setup)
│   └── work/                   # Work Google account credentials
│       ├── credentials.json    # OAuth client config (from Google Cloud Console)
│       └── token.json          # Auth token (generated during setup)
├── Dockerfile                  # Builds markonfire/mcp-youtube image
└── ACCOUNT_SEPARATION.md       # This file
```

### How It Connects to Claude

Each account is registered as a separate MCP server in `~/.claude.json`. Claude launches a fresh Docker container per session using `docker run --rm -i`, mounting the appropriate credentials directory:

```json
"youtube-personal": {
  "command": "docker",
  "args": [
    "run", "--rm", "-i",
    "-v", "~/Developer/mcp-servers/youtube-mcp/credentials/personal:/app/credentials",
    "-e", "GOOGLE_CREDENTIALS_PATH=/app/credentials/credentials.json",
    "-e", "GOOGLE_TOKEN_PATH=/app/credentials/token.json",
    "markonfire/mcp-youtube:latest"
  ],
  "type": "stdio"
}
```

Credentials are **never baked into the Docker image** — they're bind-mounted at runtime.

## Safety Measures

### 0. Destructive Operations Disabled (Both Accounts)
The `deleteVideo` and `deletePlaylist` tools are **disabled by default** for BOTH accounts. If called, they return a safety error explaining alternatives:
- Use `updateVideoMetadata` to set videos to 'private'
- Delete manually via YouTube Studio (studio.youtube.com)

To re-enable (not recommended), modify the tools in `src/server.ts` and rebuild.

### 1. Separate OAuth Credentials
Each account uses its own Google Cloud Project OAuth credentials:
- Personal account can only access personal YouTube channel
- Work account can only access work YouTube channels (including Brand Accounts)
- **No possibility of cross-account access at the API level**

### 2. Distinct MCP Server Names
Tools are clearly prefixed in Claude:
- `youtube-personal__listPlaylists` — Personal account tools
- `youtube-work__listPlaylists` — Work account tools

### 3. Brand Account Support
The PBS Wisconsin channel may be a Brand Account. The YouTube API handles this transparently — the OAuth token grants access to all channels the authenticated Google account manages, including Brand Account channels. Use `getChannelInfo` to verify which channel is active.

## Setup Instructions

### Step 1: Create Google Cloud Projects

You need **two separate Google Cloud Projects** (one for personal, one for work):

1. Go to [Google Cloud Console](https://console.cloud.google.com/)
2. Create a new project (e.g., "Claude YouTube - Personal")
3. Enable the [YouTube Data API v3](https://console.cloud.google.com/apis/library/youtube.googleapis.com)
4. Configure OAuth consent screen (External, add yourself as test user)
5. Create OAuth 2.0 Desktop Client credentials
6. Download the JSON

Repeat for your work account with a separate project.

### Step 2: Place Credentials

```bash
# Personal account
cp ~/Downloads/client_secret_xxx.json \
   ~/Developer/mcp-servers/youtube-mcp/credentials/personal/credentials.json

# Work account
cp ~/Downloads/client_secret_yyy.json \
   ~/Developer/mcp-servers/youtube-mcp/credentials/work/credentials.json
```

### Step 3: Build the Docker Image

```bash
cd ~/Developer/the-lodge
docker compose build youtube-personal
```

This builds the `markonfire/mcp-youtube:latest` image (shared by both accounts).

### Step 4: Authorize Each Account

**Option A: Token generation script (recommended)**

```bash
cd ~/Developer/the-lodge
python3 scripts/generate_youtube_token.py personal
python3 scripts/generate_youtube_token.py work
# Or: python3 scripts/generate_youtube_token.py both
```

**Option B: Docker interactive auth**

```bash
# Personal account
docker run --rm -it \
  -v ~/Developer/mcp-servers/youtube-mcp/credentials/personal:/app/credentials \
  -e GOOGLE_CREDENTIALS_PATH=/app/credentials/credentials.json \
  -e GOOGLE_TOKEN_PATH=/app/credentials/token.json \
  markonfire/mcp-youtube:latest

# Visit the URL, sign in, paste the auth code
# After "Token stored", Ctrl+C

# Work account
docker run --rm -it \
  -v ~/Developer/mcp-servers/youtube-mcp/credentials/work:/app/credentials \
  -e GOOGLE_CREDENTIALS_PATH=/app/credentials/credentials.json \
  -e GOOGLE_TOKEN_PATH=/app/credentials/token.json \
  markonfire/mcp-youtube:latest

# Visit the URL, sign in with WORK account, paste the auth code
```

### Step 5: Verify

Start a new Claude Code session and test:
- `mcp__youtube-personal__listPlaylists` — should list personal playlists
- `mcp__youtube-work__getChannelInfo` — should show work channel details

## Quota Budget

The YouTube Data API v3 has a **10,000 unit/day** quota per project. Key costs:

| Operation | Quota Cost |
|-----------|-----------|
| `listPlaylists`, `getPlaylist`, `listPlaylistItems` | 1 unit |
| `getVideoDetails`, `getVideoCategories`, `getChannelInfo` | 1 unit |
| `createPlaylist`, `addToPlaylist`, `removeFromPlaylist` | 50 units |
| `updateVideoMetadata`, `setVideoThumbnail`, `reorderPlaylistItem` | 50 units |
| `searchVideos`, `listChannelVideos` | 100 units |

**Best practices:**
- Use `getVideoDetails` (1 unit) instead of `searchVideos` (100 units) when you have video IDs
- Cache search results rather than repeating searches
- Monitor usage at [Google Cloud Console > APIs & Services > YouTube Data API v3](https://console.cloud.google.com/apis/api/youtube.googleapis.com/quotas)

## Usage Guidelines

### When to Use Personal Account
- Personal playlists and knowledge curation
- Side project video research
- Personal channel management

### When to Use Work Account
- PBS Wisconsin channel management
- Content scheduling and metadata updates
- Brand Account playlist management
- Any content that belongs to your employer

## New Machine Setup

1. Download `credentials.json` from Google Cloud Console for each account
2. Place them in `credentials/personal/` and `credentials/work/`
3. Build the image: `docker compose build youtube-personal`
4. Run the auth flow (Step 4 above)

## Troubleshooting

### "credentials.json not found"
Ensure you've placed the OAuth client config in the correct credentials directory.

### "Token expired" or re-auth prompts
Delete the `token.json` and re-run authorization (Step 4).

### "quotaExceeded" errors
You've hit the 10,000 unit daily limit. Wait until midnight Pacific time for reset, or request a quota increase in Google Cloud Console.

### Wrong channel accessed
Use `getChannelInfo` to verify which channel is active. For Brand Accounts, the OAuth token accesses the channel associated with the authenticated Google account.
