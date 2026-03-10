# YouTube MCP Server

An MCP (Model Context Protocol) server for YouTube playlist management, video discovery, and metadata operations. Built with [FastMCP](https://github.com/jlowin/fastmcp), [googleapis](https://github.com/googleapis/google-api-nodejs-client), and [Zod](https://github.com/colinhacks/zod).

## Features

- **16 tools** across playlist management, video discovery, and video metadata
- **Dual-account deployment** (personal + work) via Docker
- **Safety guardrails**: `deleteVideo` and `deletePlaylist` disabled by default
- **Brand Account support** for managed YouTube channels

## Quick Start

```bash
# Build
cd ~/Developer/the-lodge
docker compose build youtube-personal

# Authorize (browser-based OAuth)
python3 scripts/generate_youtube_token.py personal

# Verify in Claude Code
# mcp__youtube-personal__listPlaylists
```

See [ACCOUNT_SEPARATION.md](ACCOUNT_SEPARATION.md) for full setup instructions.

## Tool Reference

### Playlist Management

| Tool | Description | Quota |
|------|-------------|-------|
| `listPlaylists` | List playlists for authenticated channel or by channel ID | 1 |
| `getPlaylist` | Get details for a specific playlist | 1 |
| `createPlaylist` | Create a new playlist (title, description, privacy) | 50 |
| `deletePlaylist` | **Disabled** — delete via YouTube Studio | — |
| `listPlaylistItems` | List videos in a playlist with positions | 1 |
| `addToPlaylist` | Add a video to a playlist at optional position | 50 |
| `removeFromPlaylist` | Remove a video by playlist item ID | 50 |
| `reorderPlaylistItem` | Move a video to a new position in a playlist | 50 |

### Video Discovery

| Tool | Description | Quota |
|------|-------------|-------|
| `listChannelVideos` | List videos from a channel (expensive — use sparingly) | 100 |
| `getVideoDetails` | Full metadata, stats, and status for a video | 1 |
| `searchVideos` | Search YouTube by query with filters | 100 |

### Video Metadata

| Tool | Description | Quota |
|------|-------------|-------|
| `updateVideoMetadata` | Update title, description, tags, category, privacy | 50 |
| `setVideoThumbnail` | Upload a custom thumbnail (base64 image) | 50 |
| `getVideoCategories` | List available video categories by region | 1 |
| `deleteVideo` | **Disabled** — delete via YouTube Studio | — |
| `getChannelInfo` | Channel details, subscriber count, uploads playlist | 1 |

## Architecture

```
youtube-mcp/
├── src/
│   ├── auth.ts          # Google OAuth2 + service account auth
│   ├── server.ts        # FastMCP server with 16 YouTube tools
│   └── types.ts         # Zod parameter schemas
├── credentials/
│   ├── personal/        # Personal account OAuth credentials
│   └── work/            # Work account OAuth credentials
├── index.js             # Entry point
├── package.json
├── tsconfig.json
└── Dockerfile           # Multi-stage Node.js build
```

## Quota Budget

The YouTube Data API v3 allows **10,000 units/day** per Google Cloud project. Budget carefully:

- **Read operations** (`list`, `get`): 1 unit each
- **Write operations** (`insert`, `update`, `delete`): 50 units each
- **Search operations**: 100 units each

At typical usage (50 reads + 10 writes + 5 searches), you'll use ~1,050 units/day — well within limits.

## Development

```bash
# Install dependencies
cd ~/Developer/mcp-servers/youtube-mcp
npm install

# Build TypeScript
npm run build

# Rebuild Docker image
cd ~/Developer/the-lodge
docker compose build youtube-personal
```

## Related

- [google-docs-mcp](../google-docs-mcp/) — Google Docs/Drive/Sheets MCP server (same auth pattern)
- [google-analytics-mcp](../google-analytics-mcp/) — Google Analytics MCP server
- [YouTube Data API v3 docs](https://developers.google.com/youtube/v3)
