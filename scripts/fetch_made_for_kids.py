"""
Fetch madeForKids status for all videos in the database.
Outputs a CSV with video_id, title, show_name, madeForKids, selfDeclaredMadeForKids.
"""

import sqlite3
import csv
import sys
import os
import time

# Add project root to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.youtube_api.auth import get_authenticated_service


def fetch_made_for_kids():
    # Get YouTube Data API client
    youtube = get_authenticated_service()

    # Get all video IDs and metadata from database
    conn = sqlite3.connect("data/youtube_analytics.db")
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    cursor.execute("""
        SELECT video_id, title, show_name, channel_id, duration_minutes,
               is_short, views, views_per_day, published_at, content_type
        FROM videos
        ORDER BY channel_id, show_name, title
    """)
    videos = [dict(row) for row in cursor.fetchall()]
    conn.close()

    print(f"Fetching madeForKids status for {len(videos)} videos...", file=sys.stderr)

    # Build lookup dict
    video_lookup = {v["video_id"]: v for v in videos}

    # Batch query YouTube API (50 IDs per request)
    all_ids = [v["video_id"] for v in videos]
    batch_size = 50
    results = []
    api_calls = 0

    for i in range(0, len(all_ids), batch_size):
        batch = all_ids[i : i + batch_size]
        try:
            response = youtube.videos().list(
                part="status",
                id=",".join(batch),
            ).execute()
            api_calls += 1

            for item in response.get("items", []):
                vid = item["id"]
                status = item.get("status", {})
                meta = video_lookup.get(vid, {})
                results.append({
                    "video_id": vid,
                    "title": meta.get("title", ""),
                    "show_name": meta.get("show_name", ""),
                    "channel_id": meta.get("channel_id", ""),
                    "duration_minutes": meta.get("duration_minutes", 0),
                    "is_short": meta.get("is_short", False),
                    "views": meta.get("views", 0),
                    "views_per_day": meta.get("views_per_day", 0),
                    "published_at": meta.get("published_at", ""),
                    "content_type": meta.get("content_type", ""),
                    "made_for_kids": status.get("madeForKids", None),
                    "self_declared_made_for_kids": status.get("selfDeclaredMadeForKids", None),
                })

            # Progress
            if api_calls % 10 == 0:
                print(f"  ...{api_calls} API calls, {len(results)} videos processed", file=sys.stderr)

        except Exception as e:
            print(f"Error on batch {i}-{i+batch_size}: {e}", file=sys.stderr)
            time.sleep(2)
            continue

    print(f"Done: {api_calls} API calls, {len(results)} videos with status", file=sys.stderr)

    # Find videos in DB but not returned by API (deleted/private)
    returned_ids = {r["video_id"] for r in results}
    missing = [vid for vid in all_ids if vid not in returned_ids]
    if missing:
        print(f"Note: {len(missing)} videos not returned by API (deleted/private)", file=sys.stderr)

    # Write CSV
    output_path = "reports/made_for_kids_audit.csv"
    os.makedirs("reports", exist_ok=True)
    fieldnames = [
        "video_id", "title", "show_name", "channel_id", "duration_minutes",
        "is_short", "views", "views_per_day", "published_at", "content_type",
        "made_for_kids", "self_declared_made_for_kids",
    ]
    with open(output_path, "w", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(results)

    print(f"Wrote {len(results)} rows to {output_path}", file=sys.stderr)

    # Quick summary
    kids_true = sum(1 for r in results if r["made_for_kids"] is True)
    kids_false = sum(1 for r in results if r["made_for_kids"] is False)
    kids_none = sum(1 for r in results if r["made_for_kids"] is None)
    print(f"\nSummary:", file=sys.stderr)
    print(f"  Made for Kids = True:  {kids_true}", file=sys.stderr)
    print(f"  Made for Kids = False: {kids_false}", file=sys.stderr)
    print(f"  Made for Kids = None:  {kids_none}", file=sys.stderr)

    # Show breakdown by show_name for made_for_kids=True
    if kids_true > 0:
        print(f"\nShows with Made for Kids = True:", file=sys.stderr)
        show_counts = {}
        for r in results:
            if r["made_for_kids"] is True:
                show = r["show_name"] or "(no show)"
                show_counts[show] = show_counts.get(show, 0) + 1
        for show, count in sorted(show_counts.items(), key=lambda x: -x[1]):
            print(f"  {show}: {count}", file=sys.stderr)


if __name__ == "__main__":
    fetch_made_for_kids()
