"""
YouTube API Data Loader.
Drop-in replacement for CSV-based DataLoader that fetches from YouTube API.
"""

import logging
from datetime import datetime, timedelta
from typing import Optional, Tuple, Dict, Any, List

import pandas as pd
import numpy as np

from .client import YouTubeAPIClient
from .show_parser import extract_show_name, normalize_show_name  # noqa: F401

logger = logging.getLogger(__name__)


class YouTubeAPIDataLoader:
    """
    Loads YouTube data via API, providing same interface as CSV DataLoader.
    """

    def __init__(
        self,
        channel_id: Optional[str] = None,
        credentials_path: Optional[str] = None,
        token_path: Optional[str] = None,
        lookback_days: int = 540  # ~18 months
    ):
        """
        Initialize the API-based data loader.

        Args:
            channel_id: YouTube channel ID (uses authenticated user's if None)
            credentials_path: Path to OAuth credentials
            token_path: Path to token storage
            lookback_days: How far back to fetch analytics (default ~18 months)
        """
        self.channel_id = channel_id
        self.lookback_days = lookback_days
        self.client = YouTubeAPIClient(credentials_path, token_path)

        self.videos_df: Optional[pd.DataFrame] = None
        self.subscribers_df: Optional[pd.DataFrame] = None
        self._channel_info: Optional[Dict[str, Any]] = None

    def load_videos_data(self) -> pd.DataFrame:
        """
        Load video data from YouTube API.

        Returns:
            Processed videos DataFrame matching CSV loader format
        """
        logger.info("Fetching videos from YouTube API...")

        # Get all videos
        videos = self.client.get_all_videos(self.channel_id)
        logger.info(f"Fetched {len(videos)} videos from API")

        # Convert to DataFrame with expected columns
        self.videos_df = pd.DataFrame(videos)

        # Rename columns to match existing format
        self.videos_df = self.videos_df.rename(columns={
            'title': 'Title',
            'published_at': 'Publish Date',
            'views': 'Views',
            'likes': 'Likes',
            'comments': 'Comments',
            'duration_minutes': 'Duration (minutes)'
        })

        # Parse dates (strip timezone to match CSV loader's tz-naive format)
        self.videos_df['Publish Date'] = pd.to_datetime(
            self.videos_df['Publish Date'], utc=True
        ).dt.tz_localize(None)

        # Sort by date
        self.videos_df = self.videos_df.sort_values('Publish Date')

        # Add computed metrics (matching CSV loader)
        self._preprocess_videos_data()

        # Add PBS-specific fields
        self.videos_df['Show Name'] = self.videos_df['Title'].apply(extract_show_name)

        # Classify content types via Analytics API (authoritative)
        self.classify_content_types()

        self.videos_df['Is Short'] = self.videos_df['is_short']
        self.videos_df['Content Type'] = self.videos_df['content_type']

        logger.info("Videos data preprocessing completed")
        return self.videos_df

    def load_subscribers_data(self) -> Optional[pd.DataFrame]:
        """
        Load subscriber data from YouTube Analytics API.

        Returns:
            Processed subscribers DataFrame matching CSV loader format
        """
        try:
            logger.info("Fetching subscriber analytics from YouTube API...")

            end_date = (datetime.now() - timedelta(days=1)).strftime('%Y-%m-%d')
            start_date = (datetime.now() - timedelta(days=self.lookback_days)).strftime('%Y-%m-%d')

            analytics = self.client.get_channel_analytics(start_date, end_date)

            if not analytics:
                logger.warning("No subscriber analytics available")
                return None

            # Convert to DataFrame with expected columns
            self.subscribers_df = pd.DataFrame(analytics)

            # Rename columns to match existing format
            self.subscribers_df = self.subscribers_df.rename(columns={
                'date': 'Date',
                'subscribers_gained': 'Subscribers Gained',
                'subscribers_lost': 'Subscribers Lost',
                'engaged_views': 'Engaged Views',
            })

            # Parse dates
            self.subscribers_df['Date'] = pd.to_datetime(self.subscribers_df['Date'])

            # Sort by date
            self.subscribers_df = self.subscribers_df.sort_values('Date')

            # Add computed metrics (matching CSV loader)
            self._preprocess_subscribers_data()

            logger.info(f"Loaded {len(self.subscribers_df)} days of subscriber data")
            return self.subscribers_df

        except Exception as e:
            logger.error(f"Error loading subscribers data: {e}")
            return None

    def _preprocess_videos_data(self) -> None:
        """Preprocess videos data with calculated metrics."""
        # Calculate engagement metrics
        self.videos_df['Like Rate (%)'] = (
            self.videos_df['Likes'] / self.videos_df['Views'].replace(0, np.nan)
        ) * 100

        self.videos_df['Comment Rate (%)'] = (
            self.videos_df['Comments'] / self.videos_df['Views'].replace(0, np.nan)
        ) * 100

        self.videos_df['Engagement Rate (%)'] = (
            (self.videos_df['Likes'] + self.videos_df['Comments']) /
            self.videos_df['Views'].replace(0, np.nan)
        ) * 100

        # Handle any infinite or NaN values
        self.videos_df = self.videos_df.replace([np.inf, -np.inf], np.nan)
        self.videos_df = self.videos_df.fillna(0)

        # Add additional derived metrics
        self.videos_df['Days Since Publication'] = (
            datetime.now() - self.videos_df['Publish Date']
        ).dt.days

        self.videos_df['Views per Day'] = self.videos_df['Views'] / (
            self.videos_df['Days Since Publication'] + 1
        )

    def _preprocess_subscribers_data(self) -> None:
        """Preprocess subscribers data."""
        # Calculate net subscribers if not present
        if 'Net Subscribers' not in self.subscribers_df.columns:
            self.subscribers_df['Net Subscribers'] = (
                self.subscribers_df['Subscribers Gained'] -
                self.subscribers_df['Subscribers Lost']
            )

        # Calculate cumulative metrics
        self.subscribers_df['Cumulative Net Growth'] = (
            self.subscribers_df['Net Subscribers'].cumsum()
        )

        self.subscribers_df['Growth Rate (%)'] = (
            self.subscribers_df['Subscribers Gained'] /
            (self.subscribers_df['Subscribers Gained'] +
             self.subscribers_df['Subscribers Lost']).replace(0, np.nan)
        ) * 100

        # Handle any infinite or NaN values
        self.subscribers_df = self.subscribers_df.replace([np.inf, -np.inf], np.nan)
        self.subscribers_df = self.subscribers_df.fillna(0)

    def classify_content_types(self) -> None:
        """Enrich videos DataFrame with authoritative content type from Analytics API.

        Queries the creatorContentType dimension and updates the content_type
        and is_short columns. Videos not found in Analytics API results keep
        their duration-based heuristic classification.
        """
        if self.videos_df is None or self.videos_df.empty:
            return

        try:
            end_date = (datetime.now() - timedelta(days=1)).strftime('%Y-%m-%d')
            start_date = (
                datetime.now() - timedelta(days=self.lookback_days)
            ).strftime('%Y-%m-%d')

            classification = self.client.get_content_type_classification(
                start_date=start_date,
                end_date=end_date
            )

            if not classification:
                logger.warning("No content type classification data returned")
                return

            # Map classifications onto DataFrame
            self.videos_df['content_type'] = self.videos_df['video_id'].map(
                classification
            ).fillna('UNSPECIFIED')

            # Update is_short based on authoritative classification
            classified_mask = self.videos_df['content_type'] != 'UNSPECIFIED'
            self.videos_df.loc[classified_mask, 'is_short'] = (
                self.videos_df.loc[classified_mask, 'content_type'] == 'SHORTS'
            )

            classified_count = classified_mask.sum()
            total_count = len(self.videos_df)
            unclassified_count = total_count - classified_count
            logger.info(
                f"Classified {classified_count}/{total_count} videos "
                f"via Analytics API creatorContentType"
            )
            if unclassified_count > 0:
                logger.info(
                    f"{unclassified_count} videos outside analytics window "
                    f"({self.lookback_days} days) — using duration heuristic"
                )

        except Exception as e:
            logger.warning(
                f"Content type classification failed, using duration heuristic: {e}"
            )

    def load_all_data(self) -> Tuple[pd.DataFrame, Optional[pd.DataFrame]]:
        """
        Load both videos and subscribers data.

        Returns:
            Tuple of (videos_df, subscribers_df)
        """
        videos_df = self.load_videos_data()
        subscribers_df = self.load_subscribers_data()
        return videos_df, subscribers_df

    def get_channel_info(self) -> Dict[str, Any]:
        """Get channel metadata."""
        if self._channel_info is None:
            self._channel_info = self.client.get_channel_info(self.channel_id)
        return self._channel_info

    def get_data_summary(self) -> Dict[str, Any]:
        """
        Get summary information about loaded data.

        Returns:
            Dictionary with data summary statistics
        """
        summary = {}

        if self.videos_df is not None:
            summary['videos'] = {
                'count': len(self.videos_df),
                'date_range': {
                    'start': self.videos_df['Publish Date'].min().strftime('%Y-%m-%d'),
                    'end': self.videos_df['Publish Date'].max().strftime('%Y-%m-%d')
                },
                'total_views': int(self.videos_df['Views'].sum()),
                'total_likes': int(self.videos_df['Likes'].sum()),
                'total_comments': int(self.videos_df['Comments'].sum()),
                'avg_engagement_rate': float(self.videos_df['Engagement Rate (%)'].mean()),
                'shorts_count': int(self.videos_df['Is Short'].sum()),
                'longform_count': int((~self.videos_df['Is Short']).sum()),
                'shows': self.videos_df['Show Name'].value_counts().to_dict()
            }

        if self.subscribers_df is not None:
            summary['subscribers'] = {
                'count': len(self.subscribers_df),
                'date_range': {
                    'start': self.subscribers_df['Date'].min().strftime('%Y-%m-%d'),
                    'end': self.subscribers_df['Date'].max().strftime('%Y-%m-%d')
                },
                'total_gained': int(self.subscribers_df['Subscribers Gained'].sum()),
                'total_lost': int(self.subscribers_df['Subscribers Lost'].sum()),
                'net_growth': int(self.subscribers_df['Net Subscribers'].sum())
            }

        return summary

    # === Compatibility Methods (match CSV DataLoader interface) ===

    def validate_data_quality(self) -> Dict[str, Any]:
        """
        Validate data quality and return issues found.

        Returns:
            Dictionary with data quality report
        """
        quality_report = {
            'videos': {'issues': [], 'quality_score': 100},
            'subscribers': {'issues': [], 'quality_score': 100}
        }

        if self.videos_df is not None:
            missing_values = self.videos_df.isnull().sum()
            if missing_values.any():
                quality_report['videos']['issues'].append(
                    f"Missing values found: {missing_values[missing_values > 0].to_dict()}"
                )
                quality_report['videos']['quality_score'] -= 10

            q1 = self.videos_df['Views'].quantile(0.25)
            q3 = self.videos_df['Views'].quantile(0.75)
            iqr = q3 - q1
            outliers = self.videos_df[
                (self.videos_df['Views'] < q1 - 1.5 * iqr) |
                (self.videos_df['Views'] > q3 + 1.5 * iqr)
            ]
            if len(outliers) > 0:
                quality_report['videos']['issues'].append(
                    f"Found {len(outliers)} potential outliers in views"
                )
                quality_report['videos']['quality_score'] -= 5

        if self.subscribers_df is not None:
            if (self.subscribers_df['Subscribers Gained'] < 0).any():
                quality_report['subscribers']['issues'].append(
                    "Negative values found in Subscribers Gained"
                )
                quality_report['subscribers']['quality_score'] -= 15

            if (self.subscribers_df['Subscribers Lost'] < 0).any():
                quality_report['subscribers']['issues'].append(
                    "Negative values found in Subscribers Lost"
                )
                quality_report['subscribers']['quality_score'] -= 15

        return quality_report

    def export_processed_data(self, output_dir: str = "data/exports") -> None:
        """
        Export processed data to CSV files.

        Args:
            output_dir: Directory to save exported files
        """
        from pathlib import Path

        output_path = Path(output_dir)
        output_path.mkdir(parents=True, exist_ok=True)

        if self.videos_df is not None:
            videos_export_path = output_path / "processed_videos.csv"
            self.videos_df.to_csv(videos_export_path, index=False)
            logger.info(f"Exported processed videos data to {videos_export_path}")

        if self.subscribers_df is not None:
            subscribers_export_path = output_path / "processed_subscribers.csv"
            self.subscribers_df.to_csv(subscribers_export_path, index=False)
            logger.info(f"Exported processed subscribers data to {subscribers_export_path}")

    # === PBS Wisconsin Custom Methods ===

    def get_archival_performance(
        self,
        months_threshold: int = 12,
        recent_days: int = 30
    ) -> pd.DataFrame:
        """
        Identify high-performing archival content.

        Args:
            months_threshold: Videos older than this are 'archival'
            recent_days: Window for 'recent' performance

        Returns:
            DataFrame of archival videos with recent performance metrics
        """
        if self.videos_df is None:
            self.load_videos_data()

        cutoff_date = datetime.now() - timedelta(days=months_threshold * 30)

        archival = self.videos_df[
            self.videos_df['Publish Date'] < cutoff_date
        ].copy()

        # Calculate views per day as a velocity metric
        archival['Age (months)'] = (
            (datetime.now() - archival['Publish Date']).dt.days / 30
        ).round(1)

        # Sort by views per day (recent velocity)
        archival = archival.sort_values('Views per Day', ascending=False)

        return archival[[
            'Title', 'Show Name', 'Publish Date', 'Age (months)',
            'Views', 'Views per Day', 'Engagement Rate (%)', 'Is Short'
        ]]

    def get_shorts_summary(self) -> Dict[str, Any]:
        """
        Get summary statistics for Shorts vs longform content.

        Returns:
            Dict with comparative metrics
        """
        if self.videos_df is None:
            self.load_videos_data()

        shorts = self.videos_df[self.videos_df['Is Short'] == True]
        longform = self.videos_df[self.videos_df['Is Short'] == False]

        return {
            'shorts': {
                'count': len(shorts),
                'total_views': int(shorts['Views'].sum()),
                'avg_views': float(shorts['Views'].mean()) if len(shorts) > 0 else 0,
                'avg_engagement': float(shorts['Engagement Rate (%)'].mean()) if len(shorts) > 0 else 0,
            },
            'longform': {
                'count': len(longform),
                'total_views': int(longform['Views'].sum()),
                'avg_views': float(longform['Views'].mean()) if len(longform) > 0 else 0,
                'avg_engagement': float(longform['Engagement Rate (%)'].mean()) if len(longform) > 0 else 0,
            }
        }

    def get_show_breakdown(self) -> pd.DataFrame:
        """
        Get performance breakdown by show.

        Returns:
            DataFrame with per-show aggregate metrics
        """
        if self.videos_df is None:
            self.load_videos_data()

        breakdown = self.videos_df.groupby('Show Name').agg({
            'video_id': 'count',
            'Views': 'sum',
            'Likes': 'sum',
            'Comments': 'sum',
            'Engagement Rate (%)': 'mean',
            'Is Short': 'sum'
        }).rename(columns={
            'video_id': 'Video Count',
            'Is Short': 'Shorts Count'
        })

        breakdown['Avg Views'] = (breakdown['Views'] / breakdown['Video Count']).round(0)
        breakdown = breakdown.sort_values('Views', ascending=False)

        return breakdown

    def get_subscriber_sources_by_content_type(self) -> Dict[str, Any]:
        """
        Get subscriber acquisition breakdown by content type.

        Returns:
            Dict with subscriber sources by Shorts vs longform
        """
        # Fetch subscriber sources from API
        sources = self.client.get_subscriber_sources()

        if self.videos_df is None:
            self.load_videos_data()

        # Create video_id to is_short mapping
        short_ids = set(
            self.videos_df[self.videos_df['Is Short'] == True]['video_id'].tolist()
        )

        shorts_subs = 0
        longform_subs = 0

        for source in sources:
            video_id = source['video_id']
            net = source['net_subscribers']

            if video_id in short_ids:
                shorts_subs += net
            else:
                longform_subs += net

        return {
            'from_shorts': shorts_subs,
            'from_longform': longform_subs,
            'total': shorts_subs + longform_subs,
            'shorts_percentage': (
                shorts_subs / (shorts_subs + longform_subs) * 100
                if (shorts_subs + longform_subs) > 0 else 0
            )
        }
