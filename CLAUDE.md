# PBS Wisconsin YouTube Analytics

## Project Overview

Custom fork of YouTubeStudioDataAnalytics that replaces CSV-based workflows with direct YouTube API integration, adding PBS Wisconsin-specific features like title pattern parsing, Shorts detection, archival content tracking, and show-based analytics aggregation.

## Technical Stack

- **Language**: Python 3.9+ (analytics), TypeScript (MCP server)
- **Frameworks**: Streamlit (dashboards), Pandas (data analysis), FastMCP (MCP server)
- **APIs**: YouTube Data API v3, YouTube Analytics API
- **Storage**: SQLite (historical data), macOS Keychain (OAuth tokens)
- **Data Models**: Pydantic for validation and serialization

## Development Commands

- **Setup**: `python -m src.youtube_api.auth` (OAuth setup, first time only)
- **Run**: `python main.py --streamlit` (interactive dashboard)
- **Test**: `pytest tests/` (when tests are implemented)
- **Virtual Environment**: `source venv/bin/activate`
- **MCP Server Build**: `cd mcp-server && npm run build`
- **MCP Token Generation**: `python scripts/generate_youtube_token.py work|personal|both`

## Available MCP Servers

This project integrates with workspace-wide MCP servers:

- **The Library** (`the-library`): Access YouTube API documentation and best practices scraped into the knowledge base
- **Airtable** (`airtable`): Query PBS Wisconsin show metadata, video taxonomy, and content planning tables
- **Readwise** (`readwise`): Save analytics insights and performance reports for later review
- **Obsidian Vault** (`obsidian-vault`): Link analytics sessions to PARA project notes for PBS Wisconsin content strategy

### Agent Workflow Guidance

When working in this repo:

1. **Before API changes**: Check The Library for YouTube API rate limit patterns and quota management strategies
2. **For show taxonomy**: Query Airtable MCP for PBS Wisconsin show naming conventions and content categories
3. **During analysis**: Save significant insights to Readwise for retrospectives
4. **For planning**: Update Obsidian project notes in `1 - Projects/PBSWI/YouTube Analytics` with session findings

## Quick Start

```bash
# Activate the virtual environment
source venv/bin/activate

# Run OAuth setup (first time only)
python -m src.youtube_api.auth

# Run the Streamlit dashboard
python main.py --streamlit
```

## Setup

### 1. Google Cloud Project Setup

1. Go to [Google Cloud Console](https://console.cloud.google.com/)
2. Create a new project or select existing
3. Enable these APIs:
   - YouTube Data API v3
   - YouTube Analytics API
4. Go to **Credentials > Create Credentials > OAuth Client ID**
5. Select **Desktop application**
6. Download the JSON credentials
7. Save as `credentials/work/credentials.json`

### 2. OAuth Authentication

```bash
source venv/bin/activate
python -m src.youtube_api.auth
```

This opens a browser for Google OAuth consent. After approval, tokens are saved to `credentials/work/token-analytics.json`.

### 3. Configure Channels

Edit `config/channels.yaml` to add your channel IDs:

```yaml
channels:
  - id: "UCxxxxxxxxxx"
    name: "PBS Wisconsin"
    type: "main"
```

## Architecture

### YouTube API Integration

The `src/youtube_api/` module provides:

- **`auth.py`**: OAuth2 flow for YouTube APIs
- **`client.py`**: YouTube Data API v3 + Analytics API client
- **`data_loader.py`**: Drop-in replacement for CSV loader
- **`models.py`**: Pydantic data models
- **`database.py`**: SQLite persistence for historical data

### Key Features (PBS Wisconsin Customizations)

1. **Title Pattern Parser**: Extracts show names from titles
   - Standard: `"Video Title | SHOW NAME"` → "SHOW NAME"
   - Exception: `"Wisconsin Life | Video Title"` → "Wisconsin Life"

2. **Shorts Detection**: Videos ≤ 60 seconds flagged as Shorts

3. **Archival Content Tracking**: Surface older content performing well

4. **Show-based Analytics**: Group metrics by show/series

## Usage

### Using the API Data Loader

```python
from src.youtube_api import YouTubeAPIDataLoader

# Initialize loader (uses authenticated user's channel)
loader = YouTubeAPIDataLoader()

# Load video data (replaces CSV loading)
videos_df = loader.load_videos_data()

# Load subscriber analytics
subscribers_df = loader.load_subscribers_data()

# PBS-specific methods
archival = loader.get_archival_performance(months_threshold=12)
shorts_summary = loader.get_shorts_summary()
show_breakdown = loader.get_show_breakdown()
```

### Using the Database

```python
from src.youtube_api import AnalyticsDatabase

db = AnalyticsDatabase()

# Store videos
db.upsert_videos_bulk(videos)

# Query
archival = db.get_archival_videos(months_threshold=12)
shows = db.get_show_summary()
shorts_vs_long = db.get_shorts_vs_longform()
```

### Running the Dashboard

```bash
# Streamlit (recommended)
python main.py --streamlit

# Dash alternative
python main.py --dash

# Data analysis only (no UI)
python main.py --data-only
```

## File Structure

```
pbswi-youtube-analytics/
├── credentials/              # OAuth tokens (git-ignored)
│   ├── personal/             # Personal Google account
│   │   ├── credentials.json  # OAuth client
│   │   └── token.json        # MCP read-write token
│   └── work/                 # PBS Wisconsin account
│       ├── credentials.json  # OAuth client
│       ├── token.json        # MCP read-write token
│       └── token-analytics.json # Python analytics read-only token
├── mcp-server/               # YouTube MCP server (TypeScript)
│   ├── src/
│   │   ├── auth.ts           # Google OAuth2 + service account auth
│   │   ├── server.ts         # FastMCP server with 16 YouTube tools
│   │   └── types.ts          # Zod parameter schemas
│   ├── index.js              # Entry point
│   ├── package.json
│   ├── tsconfig.json
│   └── Dockerfile            # Multi-stage Node.js build
├── scripts/                  # Shared utility scripts
│   └── generate_youtube_token.py  # MCP OAuth token generator
├── config/
│   └── channels.yaml         # Channel configuration
├── data/
│   └── youtube_analytics.db  # SQLite database
├── planning/                 # Session tracking and backlog
│   ├── README.md             # Current state and quick links
│   ├── progress.md           # Session handoff log
│   └── backlog.md            # Session scratchpad (items → GitHub Issues)
├── src/
│   ├── youtube_api/          # YouTube API integration (Python)
│   │   ├── auth.py           # OAuth flow (read-only scopes)
│   │   ├── client.py         # API client
│   │   ├── data_loader.py    # DataFrame loader
│   │   ├── database.py       # SQLite persistence
│   │   └── models.py         # Pydantic models
│   ├── analytics/            # Core analytics (original)
│   ├── dashboards/           # Streamlit/Dash apps
│   └── utils/                # Utilities
└── main.py                   # Entry point
```

### Credential Layout

The analytics Python code and the MCP TypeScript server share the same `credentials/` directory but use **separate tokens** because they request different OAuth scopes:

- **Python analytics**: read-only (`youtube.readonly`, `yt-analytics.readonly`) → `token-analytics.json`
- **MCP server**: read-write (`youtube`, `youtube.force-ssl`, `youtube.upload`) → `token.json`

The `credentials.json` (OAuth client identity) is shared per account.

## Secrets Management

OAuth credentials are stored in `credentials/` which is git-ignored.

For production use, consider storing the token in macOS Keychain:
```python
from scripts.keychain_secrets import get_secret, set_secret

# Store
set_secret('YOUTUBE_OAUTH_TOKEN', token_json)

# Retrieve
token = get_secret('YOUTUBE_OAUTH_TOKEN')
```

## API Rate Limits

YouTube Data API v3:
- 10,000 quota units per day
- List operations: 1 unit per request
- Search: 100 units per request

YouTube Analytics API:
- 200 queries per day per user
- Use database caching to minimize API calls

## Project Planning

Active development tracked in `planning/`:
- Current roadmap and priorities: `planning/backlog.md`
- Session handoff notes: `planning/progress.md`
- Project state summary: `planning/README.md`
