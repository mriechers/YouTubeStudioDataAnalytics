"""
YouTube API Client.
Fetches video metadata, channel statistics, and analytics data.
"""

import logging
from datetime import datetime, timedelta
from typing import List, Dict, Any, Optional
import re

from googleapiclient.discovery import Resource

from .auth import get_authenticated_service

logger = logging.getLogger(__name__)


def parse_duration(duration_str: str) -> float:
    """
    Parse ISO 8601 duration string to minutes.

    Args:
        duration_str: Duration like 'PT4M13S' or 'PT1H30M'

    Returns:
        Duration in minutes
    """
    if not duration_str:
        return 0.0

    # Pattern matches PT followed by optional hours, minutes, seconds
    pattern = r'PT(?:(\d+)H)?(?:(\d+)M)?(?:(\d+)S)?'
    match = re.match(pattern, duration_str)

    if not match:
        return 0.0

    hours = int(match.group(1) or 0)
    minutes = int(match.group(2) or 0)
    seconds = int(match.group(3) or 0)

    return hours * 60 + minutes + seconds / 60


def _parse_analytics_response(response: Dict[str, Any]) -> List[Dict[str, Any]]:
    """Parse a YouTube Analytics API response using columnHeaders for safety.

    The Analytics API may omit metrics (e.g., engagedViews for pre-March 2025
    date ranges). Parsing by column name instead of positional index prevents
    silent data misalignment.

    Returns:
        List of dicts, one per row, keyed by column name.
    """
    headers = [h['name'] for h in response.get('columnHeaders', [])]
    rows = []
    for row in response.get('rows', []):
        rows.append(dict(zip(headers, row)))
    return rows


class YouTubeAPIClient:
    """
    Client for interacting with YouTube Data API v3 and YouTube Analytics API.
    """

    def __init__(
        self,
        credentials_path: Optional[str] = None,
        token_path: Optional[str] = None
    ):
        """
        Initialize the YouTube API client.

        Args:
            credentials_path: Path to OAuth credentials JSON
            token_path: Path to token storage
        """
        self._youtube: Optional[Resource] = None
        self._analytics: Optional[Resource] = None
        self._credentials_path = credentials_path
        self._token_path = token_path

    @property
    def youtube(self) -> Resource:
        """Lazy-load YouTube Data API service."""
        if self._youtube is None:
            self._youtube = get_authenticated_service(
                'youtube', 'v3',
                self._credentials_path, self._token_path
            )
        return self._youtube

    @property
    def analytics(self) -> Resource:
        """Lazy-load YouTube Analytics API service."""
        if self._analytics is None:
            self._analytics = get_authenticated_service(
                'youtubeAnalytics', 'v2',
                self._credentials_path, self._token_path
            )
        return self._analytics

    def get_channel_info(self, channel_id: Optional[str] = None) -> Dict[str, Any]:
        """
        Get channel information. If no channel_id provided, gets the authenticated user's channel.

        Args:
            channel_id: Optional specific channel ID

        Returns:
            Channel metadata dict
        """
        if channel_id:
            request = self.youtube.channels().list(
                part='snippet,statistics,contentDetails',
                id=channel_id
            )
        else:
            # Get authenticated user's channel
            request = self.youtube.channels().list(
                part='snippet,statistics,contentDetails',
                mine=True
            )

        response = request.execute()

        if not response.get('items'):
            raise ValueError("No channel found")

        channel = response['items'][0]
        return {
            'id': channel['id'],
            'title': channel['snippet']['title'],
            'description': channel['snippet'].get('description', ''),
            'subscriber_count': int(channel['statistics'].get('subscriberCount', 0)),
            'video_count': int(channel['statistics'].get('videoCount', 0)),
            'view_count': int(channel['statistics'].get('viewCount', 0)),
            'uploads_playlist_id': channel['contentDetails']['relatedPlaylists']['uploads'],
            'published_at': channel['snippet']['publishedAt']
        }

    def get_all_videos(
        self,
        channel_id: Optional[str] = None,
        max_results: int = 500
    ) -> List[Dict[str, Any]]:
        """
        Get all videos from a channel.

        Args:
            channel_id: Channel ID (uses authenticated user's channel if None)
            max_results: Maximum number of videos to fetch

        Returns:
            List of video metadata dicts
        """
        # Get uploads playlist ID
        channel_info = self.get_channel_info(channel_id)
        playlist_id = channel_info['uploads_playlist_id']

        videos = []
        next_page_token = None

        while len(videos) < max_results:
            request = self.youtube.playlistItems().list(
                part='snippet,contentDetails',
                playlistId=playlist_id,
                maxResults=min(50, max_results - len(videos)),
                pageToken=next_page_token
            )
            response = request.execute()

            video_ids = [item['contentDetails']['videoId'] for item in response['items']]

            if video_ids:
                # Get detailed video info
                video_details = self._get_video_details(video_ids)
                videos.extend(video_details)

            next_page_token = response.get('nextPageToken')
            if not next_page_token:
                break

            logger.info(f"Fetched {len(videos)} videos...")

        logger.info(f"Total videos fetched: {len(videos)}")
        return videos

    def _get_video_details(self, video_ids: List[str]) -> List[Dict[str, Any]]:
        """
        Get detailed information for a list of video IDs.

        Args:
            video_ids: List of video IDs

        Returns:
            List of video detail dicts
        """
        request = self.youtube.videos().list(
            part='snippet,statistics,contentDetails',
            id=','.join(video_ids)
        )
        response = request.execute()

        videos = []
        for item in response.get('items', []):
            duration_minutes = parse_duration(item['contentDetails']['duration'])

            video = {
                'video_id': item['id'],
                'title': item['snippet']['title'],
                'description': item['snippet'].get('description', ''),
                'published_at': item['snippet']['publishedAt'],
                'channel_id': item['snippet']['channelId'],
                'channel_title': item['snippet']['channelTitle'],
                'thumbnail_url': item['snippet']['thumbnails'].get('high', {}).get('url', ''),
                'tags': item['snippet'].get('tags', []),
                'category_id': item['snippet'].get('categoryId'),
                'duration_minutes': duration_minutes,
                'duration_iso': item['contentDetails']['duration'],
                'views': int(item['statistics'].get('viewCount', 0)),
                'likes': int(item['statistics'].get('likeCount', 0)),
                'comments': int(item['statistics'].get('commentCount', 0)),
                # Duration heuristic: <= 3 min (expanded from 60s in Oct 2024).
                # Authoritative classification comes from Analytics API
                # creatorContentType dimension (see classify_content_types).
                'is_short': duration_minutes <= 3.0,
                'content_type': 'UNSPECIFIED',
            }
            videos.append(video)

        return videos

    def get_video_analytics(
        self,
        video_id: str,
        start_date: Optional[str] = None,
        end_date: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Get analytics for a specific video.

        Args:
            video_id: YouTube video ID
            start_date: Start date (YYYY-MM-DD), defaults to 90 days ago
            end_date: End date (YYYY-MM-DD), defaults to yesterday

        Returns:
            Analytics data dict
        """
        if not end_date:
            end_date = (datetime.now() - timedelta(days=1)).strftime('%Y-%m-%d')
        if not start_date:
            start_date = (datetime.now() - timedelta(days=90)).strftime('%Y-%m-%d')

        request = self.analytics.reports().query(
            ids='channel==MINE',
            startDate=start_date,
            endDate=end_date,
            metrics='views,engagedViews,estimatedMinutesWatched,averageViewDuration,subscribersGained,subscribersLost',
            dimensions='video',
            filters=f'video=={video_id}'
        )
        response = request.execute()

        parsed = _parse_analytics_response(response)

        if not parsed:
            return {
                'video_id': video_id,
                'views': 0,
                'engaged_views': None,
                'watch_time_minutes': 0,
                'avg_view_duration_seconds': 0,
                'subscribers_gained': 0,
                'subscribers_lost': 0
            }

        row = parsed[0]
        return {
            'video_id': row.get('video', video_id),
            'views': int(row.get('views', 0)),
            'engaged_views': int(row['engagedViews']) if row.get('engagedViews') is not None else None,
            'watch_time_minutes': float(row.get('estimatedMinutesWatched', 0)),
            'avg_view_duration_seconds': float(row.get('averageViewDuration', 0)),
            'subscribers_gained': int(row.get('subscribersGained', 0)),
            'subscribers_lost': int(row.get('subscribersLost', 0))
        }

    def get_channel_analytics(
        self,
        start_date: Optional[str] = None,
        end_date: Optional[str] = None,
        dimensions: str = 'day'
    ) -> List[Dict[str, Any]]:
        """
        Get channel-level analytics over time.

        Args:
            start_date: Start date (YYYY-MM-DD)
            end_date: End date (YYYY-MM-DD)
            dimensions: 'day', 'month', etc.

        Returns:
            List of daily analytics dicts
        """
        if not end_date:
            end_date = (datetime.now() - timedelta(days=1)).strftime('%Y-%m-%d')
        if not start_date:
            start_date = (datetime.now() - timedelta(days=90)).strftime('%Y-%m-%d')

        request = self.analytics.reports().query(
            ids='channel==MINE',
            startDate=start_date,
            endDate=end_date,
            metrics='views,engagedViews,estimatedMinutesWatched,averageViewDuration,subscribersGained,subscribersLost',
            dimensions=dimensions
        )
        response = request.execute()
        parsed = _parse_analytics_response(response)

        results = []
        for row in parsed:
            results.append({
                'date': row.get('day') or row.get('month', ''),
                'views': int(row.get('views', 0)),
                'engaged_views': int(row['engagedViews']) if row.get('engagedViews') is not None else None,
                'watch_time_minutes': float(row.get('estimatedMinutesWatched', 0)),
                'avg_view_duration_seconds': float(row.get('averageViewDuration', 0)),
                'subscribers_gained': int(row.get('subscribersGained', 0)),
                'subscribers_lost': int(row.get('subscribersLost', 0))
            })

        return results

    def get_traffic_sources(
        self,
        video_id: Optional[str] = None,
        start_date: Optional[str] = None,
        end_date: Optional[str] = None
    ) -> List[Dict[str, Any]]:
        """
        Get traffic source breakdown.

        Args:
            video_id: Optional video ID (channel-wide if None)
            start_date: Start date
            end_date: End date

        Returns:
            List of traffic source dicts
        """
        if not end_date:
            end_date = (datetime.now() - timedelta(days=1)).strftime('%Y-%m-%d')
        if not start_date:
            start_date = (datetime.now() - timedelta(days=90)).strftime('%Y-%m-%d')

        query_params = {
            'ids': 'channel==MINE',
            'startDate': start_date,
            'endDate': end_date,
            'metrics': 'views,estimatedMinutesWatched',
            'dimensions': 'insightTrafficSourceType'
        }

        if video_id:
            query_params['filters'] = f'video=={video_id}'

        request = self.analytics.reports().query(**query_params)
        response = request.execute()

        results = []
        for row in response.get('rows', []):
            results.append({
                'source': row[0],
                'views': int(row[1]),
                'watch_time_minutes': float(row[2])
            })

        return results

    def get_content_type_classification(
        self,
        start_date: Optional[str] = None,
        end_date: Optional[str] = None
    ) -> Dict[str, str]:
        """
        Classify videos by content type using the Analytics API creatorContentType dimension.

        This is the authoritative source for Shorts vs. longform classification.
        The Data API has no isShort flag (Google Issue Tracker #232112727).

        Args:
            start_date: Start date (YYYY-MM-DD)
            end_date: End date (YYYY-MM-DD)

        Returns:
            Dict mapping video_id -> content_type string
            (SHORTS, VIDEO_ON_DEMAND, LIVE_STREAM, STORY)
        """
        if not end_date:
            end_date = (datetime.now() - timedelta(days=1)).strftime('%Y-%m-%d')
        if not start_date:
            start_date = (datetime.now() - timedelta(days=90)).strftime('%Y-%m-%d')

        request = self.analytics.reports().query(
            ids='channel==MINE',
            startDate=start_date,
            endDate=end_date,
            metrics='views',
            dimensions='video,creatorContentType'
        )
        response = request.execute()

        classification = {}
        for row in response.get('rows', []):
            video_id = row[0]
            content_type = row[1]
            classification[video_id] = content_type

        logger.info(f"Classified {len(classification)} videos by content type")
        return classification

    def get_subscriber_sources(
        self,
        start_date: Optional[str] = None,
        end_date: Optional[str] = None
    ) -> List[Dict[str, Any]]:
        """
        Get subscriber acquisition by video.

        Args:
            start_date: Start date
            end_date: End date

        Returns:
            List of video subscriber data
        """
        if not end_date:
            end_date = (datetime.now() - timedelta(days=1)).strftime('%Y-%m-%d')
        if not start_date:
            start_date = (datetime.now() - timedelta(days=90)).strftime('%Y-%m-%d')

        request = self.analytics.reports().query(
            ids='channel==MINE',
            startDate=start_date,
            endDate=end_date,
            metrics='subscribersGained,subscribersLost',
            dimensions='video',
            sort='-subscribersGained',
            maxResults=50
        )
        response = request.execute()

        results = []
        for row in response.get('rows', []):
            results.append({
                'video_id': row[0],
                'subscribers_gained': int(row[1]),
                'subscribers_lost': int(row[2]),
                'net_subscribers': int(row[1]) - int(row[2])
            })

        return results
