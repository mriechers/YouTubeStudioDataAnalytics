"""
Tests for the YouTube API integration module.

Covers:
- extract_show_name() title parsing logic
- YouTubeAPIDataLoader interface compatibility and data quality validation
- AnalyticsDatabase CRUD operations (using temp SQLite files)
- Pydantic model validation
"""

import sys
import tempfile
from datetime import datetime, timedelta
from pathlib import Path
from unittest.mock import patch, MagicMock

import pandas as pd
import pytest

# Add project root to path so 'src' package imports work
sys.path.insert(0, str(Path(__file__).parent.parent))

from src.youtube_api.client import _parse_analytics_response
from src.youtube_api.data_loader import extract_show_name, YouTubeAPIDataLoader
from src.youtube_api.database import AnalyticsDatabase
from src.youtube_api.models import Video, ChannelStats, DailyAnalytics, VideoAnalytics, ContentType


# ---------------------------------------------------------------------------
# extract_show_name() tests
# ---------------------------------------------------------------------------

class TestExtractShowName:
    """Tests for PBS Wisconsin title pattern parsing."""

    def test_standard_pattern(self):
        """Standard: 'Video Title | SHOW NAME' -> 'SHOW NAME'."""
        assert extract_show_name("Great Episode | PBS Wisconsin") == "PBS Wisconsin"

    def test_wisconsin_life_exception(self):
        """Exception: 'Wisconsin Life | ...' -> 'Wisconsin Life'."""
        assert extract_show_name("Wisconsin Life | A Day in Madison") == "Wisconsin Life"

    def test_no_pipe(self):
        """No pipe character -> 'Uncategorized'."""
        assert extract_show_name("Just a Title") == "Uncategorized"

    def test_multiple_pipes(self):
        """Multiple pipes: takes last segment as show name."""
        assert extract_show_name("Part 1 | Part 2 | SHOW NAME") == "SHOW NAME"

    def test_empty_string(self):
        """Empty string -> 'Uncategorized'."""
        assert extract_show_name("") == "Uncategorized"

    def test_pipe_with_whitespace(self):
        """Pipe surrounded by spaces is the delimiter; plain pipe is not."""
        assert extract_show_name("No|Spaces") == "Uncategorized"

    def test_wisconsin_life_multiple_pipes(self):
        """Wisconsin Life exception still works with extra pipe segments."""
        assert extract_show_name("Wisconsin Life | Segment | Extra") == "Wisconsin Life"

    def test_trailing_whitespace(self):
        """Show name trailing whitespace is stripped."""
        assert extract_show_name("Title | SHOW NAME  ") == "SHOW NAME"


# ---------------------------------------------------------------------------
# YouTubeAPIDataLoader interface tests
# ---------------------------------------------------------------------------

class TestDataLoaderInterface:
    """Verify YouTubeAPIDataLoader exposes the methods that
    YouTubeAnalytics.run_complete_analysis() expects."""

    def test_has_load_all_data(self):
        assert hasattr(YouTubeAPIDataLoader, 'load_all_data')
        assert callable(getattr(YouTubeAPIDataLoader, 'load_all_data'))

    def test_has_get_data_summary(self):
        assert hasattr(YouTubeAPIDataLoader, 'get_data_summary')
        assert callable(getattr(YouTubeAPIDataLoader, 'get_data_summary'))

    def test_has_validate_data_quality(self):
        assert hasattr(YouTubeAPIDataLoader, 'validate_data_quality')
        assert callable(getattr(YouTubeAPIDataLoader, 'validate_data_quality'))

    def test_has_export_processed_data(self):
        assert hasattr(YouTubeAPIDataLoader, 'export_processed_data')
        assert callable(getattr(YouTubeAPIDataLoader, 'export_processed_data'))

    def test_has_load_videos_data(self):
        assert hasattr(YouTubeAPIDataLoader, 'load_videos_data')

    def test_has_load_subscribers_data(self):
        assert hasattr(YouTubeAPIDataLoader, 'load_subscribers_data')


# ---------------------------------------------------------------------------
# Content type classification tests
# ---------------------------------------------------------------------------

class TestContentTypeClassification:
    """Tests for the creatorContentType classification pipeline."""

    @patch('src.youtube_api.data_loader.YouTubeAPIClient')
    def test_classify_updates_content_type(self, mock_client_cls):
        """classify_content_types maps Analytics API results onto DataFrame."""
        loader = YouTubeAPIDataLoader.__new__(YouTubeAPIDataLoader)
        loader.client = mock_client_cls.return_value
        loader.lookback_days = 90

        # Mock the Analytics API classification response
        loader.client.get_content_type_classification.return_value = {
            'vid_001': 'SHORTS',
            'vid_002': 'VIDEO_ON_DEMAND',
        }

        loader.videos_df = pd.DataFrame({
            'video_id': ['vid_001', 'vid_002', 'vid_003'],
            'content_type': ['UNSPECIFIED', 'UNSPECIFIED', 'UNSPECIFIED'],
            'is_short': [True, False, True],  # duration heuristic
        })

        loader.classify_content_types()

        assert loader.videos_df.loc[0, 'content_type'] == 'SHORTS'
        assert loader.videos_df.loc[1, 'content_type'] == 'VIDEO_ON_DEMAND'
        # vid_003 not in API results, stays UNSPECIFIED
        assert loader.videos_df.loc[2, 'content_type'] == 'UNSPECIFIED'

    @patch('src.youtube_api.data_loader.YouTubeAPIClient')
    def test_classify_updates_is_short(self, mock_client_cls):
        """is_short is updated based on authoritative content_type."""
        loader = YouTubeAPIDataLoader.__new__(YouTubeAPIDataLoader)
        loader.client = mock_client_cls.return_value
        loader.lookback_days = 90

        loader.client.get_content_type_classification.return_value = {
            'vid_001': 'VIDEO_ON_DEMAND',  # Override: short duration but VOD
        }

        loader.videos_df = pd.DataFrame({
            'video_id': ['vid_001'],
            'content_type': ['UNSPECIFIED'],
            'is_short': [True],  # heuristic said Short
        })

        loader.classify_content_types()

        assert loader.videos_df.loc[0, 'is_short'] == False
        assert loader.videos_df.loc[0, 'content_type'] == 'VIDEO_ON_DEMAND'

    @patch('src.youtube_api.data_loader.YouTubeAPIClient')
    def test_classify_handles_api_failure(self, mock_client_cls):
        """Classification gracefully falls back when API call fails."""
        loader = YouTubeAPIDataLoader.__new__(YouTubeAPIDataLoader)
        loader.client = mock_client_cls.return_value
        loader.lookback_days = 90

        loader.client.get_content_type_classification.side_effect = Exception("quota exceeded")

        loader.videos_df = pd.DataFrame({
            'video_id': ['vid_001'],
            'content_type': ['UNSPECIFIED'],
            'is_short': [True],
        })

        # Should not raise
        loader.classify_content_types()

        # Original values preserved
        assert loader.videos_df.loc[0, 'content_type'] == 'UNSPECIFIED'
        assert loader.videos_df.loc[0, 'is_short'] == True

    @patch('src.youtube_api.data_loader.YouTubeAPIClient')
    def test_classify_empty_dataframe(self, mock_client_cls):
        """classify_content_types is a no-op on empty DataFrame."""
        loader = YouTubeAPIDataLoader.__new__(YouTubeAPIDataLoader)
        loader.client = mock_client_cls.return_value
        loader.lookback_days = 90
        loader.videos_df = pd.DataFrame()

        # Should not raise or call API
        loader.classify_content_types()
        loader.client.get_content_type_classification.assert_not_called()


# ---------------------------------------------------------------------------
# validate_data_quality() structure tests
# ---------------------------------------------------------------------------

class TestValidateDataQuality:
    """Ensure validate_data_quality() returns the expected dict shape."""

    @patch('src.youtube_api.data_loader.YouTubeAPIClient')
    def test_quality_report_structure_no_data(self, mock_client_cls):
        """With no loaded data, report has correct top-level keys and defaults."""
        loader = YouTubeAPIDataLoader.__new__(YouTubeAPIDataLoader)
        loader.videos_df = None
        loader.subscribers_df = None
        loader.client = mock_client_cls.return_value

        report = loader.validate_data_quality()

        assert 'videos' in report
        assert 'subscribers' in report
        assert report['videos']['issues'] == []
        assert report['videos']['quality_score'] == 100
        assert report['subscribers']['issues'] == []
        assert report['subscribers']['quality_score'] == 100

    @patch('src.youtube_api.data_loader.YouTubeAPIClient')
    def test_quality_report_with_clean_data(self, mock_client_cls):
        """Clean data should yield quality_score 100 (or 95 if outliers)."""
        loader = YouTubeAPIDataLoader.__new__(YouTubeAPIDataLoader)
        loader.client = mock_client_cls.return_value

        loader.videos_df = pd.DataFrame({
            'Title': ['A | Show', 'B | Show'],
            'Views': [1000, 1200],
            'Likes': [50, 60],
            'Comments': [5, 6],
        })
        loader.subscribers_df = pd.DataFrame({
            'Subscribers Gained': [10, 20],
            'Subscribers Lost': [1, 2],
        })

        report = loader.validate_data_quality()

        assert isinstance(report['videos']['issues'], list)
        assert isinstance(report['videos']['quality_score'], int)
        assert isinstance(report['subscribers']['issues'], list)
        assert isinstance(report['subscribers']['quality_score'], int)

    @patch('src.youtube_api.data_loader.YouTubeAPIClient')
    def test_quality_report_negative_subscribers(self, mock_client_cls):
        """Negative subscriber values should produce quality issues."""
        loader = YouTubeAPIDataLoader.__new__(YouTubeAPIDataLoader)
        loader.client = mock_client_cls.return_value
        loader.videos_df = None

        loader.subscribers_df = pd.DataFrame({
            'Subscribers Gained': [-5, 20],
            'Subscribers Lost': [1, 2],
        })

        report = loader.validate_data_quality()

        assert len(report['subscribers']['issues']) > 0
        assert report['subscribers']['quality_score'] < 100


# ---------------------------------------------------------------------------
# AnalyticsDatabase CRUD tests
# ---------------------------------------------------------------------------

class TestAnalyticsDatabase:
    """Tests for AnalyticsDatabase using temporary SQLite files."""

    @pytest.fixture
    def db(self, tmp_path):
        """Create a fresh database in a temp directory."""
        db_path = tmp_path / "test_analytics.db"
        return AnalyticsDatabase(db_path=db_path)

    def _make_video(self, video_id="vid_001", **overrides):
        """Helper to build a video dict with sensible defaults."""
        data = {
            'video_id': video_id,
            'title': 'Test Video | Test Show',
            'description': 'A test video',
            'published_at': datetime(2024, 6, 15),
            'channel_id': 'UC_test',
            'channel_title': 'Test Channel',
            'show_name': 'Test Show',
            'duration_minutes': 5.0,
            'is_short': False,
            'content_type': 'UNSPECIFIED',
            'views': 1000,
            'likes': 50,
            'comments': 10,
            'engagement_rate': 6.0,
            'views_per_day': 5.0,
            'days_since_publication': 200,
        }
        data.update(overrides)
        return data

    # -- upsert_video / get_all_videos --

    def test_upsert_and_retrieve_single_video(self, db):
        """Insert one video and retrieve it."""
        video = self._make_video()
        db.upsert_video(video)

        results = db.get_all_videos()
        assert len(results) == 1
        assert results[0]['video_id'] == 'vid_001'
        assert results[0]['title'] == 'Test Video | Test Show'

    def test_upsert_updates_existing_video(self, db):
        """Upserting with same video_id updates the record."""
        db.upsert_video(self._make_video(views=1000))
        db.upsert_video(self._make_video(views=2000))

        results = db.get_all_videos()
        assert len(results) == 1
        assert results[0]['views'] == 2000

    def test_get_all_videos_channel_filter(self, db):
        """get_all_videos filters by channel_id when provided."""
        db.upsert_video(self._make_video('v1', channel_id='UC_a'))
        db.upsert_video(self._make_video('v2', channel_id='UC_b'))

        results = db.get_all_videos(channel_id='UC_a')
        assert len(results) == 1
        assert results[0]['channel_id'] == 'UC_a'

    # -- upsert_videos_bulk --

    def test_bulk_upsert(self, db):
        """Bulk insert multiple videos at once."""
        videos = [
            self._make_video('v1', title='First | Show A'),
            self._make_video('v2', title='Second | Show B'),
            self._make_video('v3', title='Third | Show A'),
        ]
        count = db.upsert_videos_bulk(videos)

        assert count == 3
        assert len(db.get_all_videos()) == 3

    def test_bulk_upsert_updates_existing(self, db):
        """Bulk upsert updates records that already exist."""
        db.upsert_video(self._make_video('v1', views=100))

        updated = [self._make_video('v1', views=999)]
        db.upsert_videos_bulk(updated)

        results = db.get_all_videos()
        assert len(results) == 1
        assert results[0]['views'] == 999

    # -- add_daily_stats --

    def test_add_and_query_daily_stats(self, db):
        """Add daily stats and verify they persist."""
        date = datetime(2024, 8, 1)
        db.add_daily_stats('vid_001', date, {
            'views': 500,
            'likes': 25,
            'comments': 3,
            'watch_time_minutes': 120.5,
            'subscribers_gained': 2,
        })

        # Query via session to verify
        from src.youtube_api.database import DailyStatsTable
        with db.get_session() as session:
            row = session.query(DailyStatsTable).filter_by(video_id='vid_001').first()
            assert row is not None
            assert row.views == 500
            assert row.watch_time_minutes == 120.5

    def test_daily_stats_upsert(self, db):
        """Inserting same video_id+date updates existing stats."""
        date = datetime(2024, 8, 1)
        db.add_daily_stats('vid_001', date, {'views': 100})
        db.add_daily_stats('vid_001', date, {'views': 200})

        from src.youtube_api.database import DailyStatsTable
        with db.get_session() as session:
            rows = session.query(DailyStatsTable).filter_by(video_id='vid_001').all()
            assert len(rows) == 1
            assert rows[0].views == 200

    # -- add_channel_snapshot --

    def test_add_channel_snapshot(self, db):
        """Add a channel snapshot and retrieve it."""
        date = datetime.now() - timedelta(days=10)
        db.add_channel_snapshot('UC_test', date, {
            'subscriber_count': 50000,
            'video_count': 300,
            'view_count': 10000000,
            'daily_views': 5000,
            'daily_watch_time_minutes': 2500.0,
            'daily_subscribers_gained': 15,
            'daily_subscribers_lost': 3,
        })

        history = db.get_channel_history('UC_test', days=365)
        assert len(history) == 1
        assert history[0]['subscriber_count'] == 50000

    # -- get_archival_videos --

    def test_get_archival_videos(self, db):
        """Videos older than threshold appear in archival results."""
        old_date = datetime.now() - timedelta(days=400)
        recent_date = datetime.now() - timedelta(days=30)

        db.upsert_video(self._make_video('old', published_at=old_date))
        db.upsert_video(self._make_video('new', published_at=recent_date))

        archival = db.get_archival_videos(months_threshold=12)
        ids = [v['video_id'] for v in archival]
        assert 'old' in ids
        assert 'new' not in ids

    # -- get_show_summary --

    def test_get_show_summary(self, db):
        """Show summary aggregates correctly across videos."""
        db.upsert_videos_bulk([
            self._make_video('v1', show_name='Show A', views=1000, likes=50),
            self._make_video('v2', show_name='Show A', views=2000, likes=100),
            self._make_video('v3', show_name='Show B', views=500, likes=20),
        ])

        summary = db.get_show_summary()
        shows = {s['show_name']: s for s in summary}

        assert 'Show A' in shows
        assert 'Show B' in shows
        assert shows['Show A']['video_count'] == 2
        assert shows['Show A']['total_views'] == 3000
        assert shows['Show B']['video_count'] == 1

    # -- get_shorts_vs_longform --

    def test_shorts_vs_longform(self, db):
        """Shorts and longform stats are separated correctly."""
        db.upsert_videos_bulk([
            self._make_video('s1', is_short=True, views=5000),
            self._make_video('s2', is_short=True, views=3000),
            self._make_video('l1', is_short=False, views=10000),
        ])

        result = db.get_shorts_vs_longform()
        assert result['shorts']['count'] == 2
        assert result['shorts']['total_views'] == 8000
        assert result['longform']['count'] == 1
        assert result['longform']['total_views'] == 10000

    def test_content_type_persisted(self, db):
        """content_type column is stored and retrieved."""
        db.upsert_video(self._make_video('v1', content_type='SHORTS'))
        db.upsert_video(self._make_video('v2', content_type='VIDEO_ON_DEMAND'))

        results = db.get_all_videos()
        types = {r['video_id']: r['content_type'] for r in results}
        assert types['v1'] == 'SHORTS'
        assert types['v2'] == 'VIDEO_ON_DEMAND'

    def test_content_type_defaults_unspecified(self, db):
        """Videos without explicit content_type default to UNSPECIFIED."""
        db.upsert_video(self._make_video('v1'))

        results = db.get_all_videos()
        assert results[0]['content_type'] == 'UNSPECIFIED'


# ---------------------------------------------------------------------------
# Pydantic model tests
# ---------------------------------------------------------------------------

class TestPydanticModels:
    """Test Pydantic data model validation and computed fields."""

    def test_video_is_short_duration_heuristic(self):
        """Videos <= 3.0 minutes are Shorts (duration heuristic, expanded Oct 2024)."""
        v = Video(
            video_id='abc',
            title='Short Clip',
            published_at=datetime.now(),
            channel_id='UC_test',
            channel_title='Test',
            duration_minutes=0.5,
            duration_iso='PT30S',
        )
        assert v.is_short is True

    def test_video_is_short_2min_short(self):
        """2-minute video is a Short under the 3-min threshold."""
        v = Video(
            video_id='abc',
            title='Two Min Short',
            published_at=datetime.now(),
            channel_id='UC_test',
            channel_title='Test',
            duration_minutes=2.0,
            duration_iso='PT2M',
        )
        assert v.is_short is True

    def test_video_is_short_3min_boundary(self):
        """Exactly 3.0 minutes is still a Short (boundary case)."""
        v = Video(
            video_id='abc',
            title='3 Min Short',
            published_at=datetime.now(),
            channel_id='UC_test',
            channel_title='Test',
            duration_minutes=3.0,
            duration_iso='PT3M',
        )
        assert v.is_short is True

    def test_video_is_short_false(self):
        """Videos > 3.0 minutes are not Shorts."""
        v = Video(
            video_id='abc',
            title='Long Video',
            published_at=datetime.now(),
            channel_id='UC_test',
            channel_title='Test',
            duration_minutes=10.0,
            duration_iso='PT10M',
        )
        assert v.is_short is False

    def test_content_type_overrides_duration(self):
        """When content_type is set, it overrides duration heuristic."""
        # 10 min video classified as SHORTS by Analytics API
        v = Video(
            video_id='abc',
            title='Long But Actually Short',
            published_at=datetime.now(),
            channel_id='UC_test',
            channel_title='Test',
            duration_minutes=10.0,
            duration_iso='PT10M',
            content_type=ContentType.SHORTS,
        )
        assert v.is_short is True

    def test_content_type_vod_not_short(self):
        """VIDEO_ON_DEMAND content_type means not a Short, even if short duration."""
        v = Video(
            video_id='abc',
            title='Short VOD',
            published_at=datetime.now(),
            channel_id='UC_test',
            channel_title='Test',
            duration_minutes=0.5,
            duration_iso='PT30S',
            content_type=ContentType.VIDEO_ON_DEMAND,
        )
        assert v.is_short is False

    def test_content_type_defaults_to_unspecified(self):
        """Videos default to UNSPECIFIED content_type."""
        v = Video(
            video_id='abc',
            title='Default',
            published_at=datetime.now(),
            channel_id='UC_test',
            channel_title='Test',
            duration_minutes=5.0,
            duration_iso='PT5M',
        )
        assert v.content_type == ContentType.UNSPECIFIED

    def test_video_show_name_standard(self):
        """Video model extracts show name from standard title."""
        v = Video(
            video_id='abc',
            title='Great Content | PBS Wisconsin',
            published_at=datetime.now(),
            channel_id='UC_test',
            channel_title='Test',
            duration_minutes=5.0,
            duration_iso='PT5M',
        )
        assert v.show_name == 'PBS Wisconsin'

    def test_video_show_name_wisconsin_life(self):
        """Video model handles Wisconsin Life exception."""
        v = Video(
            video_id='abc',
            title='Wisconsin Life | Madison Farmers Market',
            published_at=datetime.now(),
            channel_id='UC_test',
            channel_title='Test',
            duration_minutes=5.0,
            duration_iso='PT5M',
        )
        assert v.show_name == 'Wisconsin Life'

    def test_video_engagement_rate_zero_views(self):
        """Engagement rate is 0.0 when views are zero."""
        v = Video(
            video_id='abc',
            title='No Views',
            published_at=datetime.now(),
            channel_id='UC_test',
            channel_title='Test',
            duration_minutes=5.0,
            duration_iso='PT5M',
            views=0,
            likes=0,
            comments=0,
        )
        assert v.engagement_rate == 0.0

    def test_video_engagement_rate_calculation(self):
        """Engagement rate = (likes + comments) / views * 100."""
        v = Video(
            video_id='abc',
            title='Popular',
            published_at=datetime.now(),
            channel_id='UC_test',
            channel_title='Test',
            duration_minutes=5.0,
            duration_iso='PT5M',
            views=1000,
            likes=80,
            comments=20,
        )
        assert v.engagement_rate == pytest.approx(10.0)

    def test_daily_analytics_net_subscribers(self):
        """DailyAnalytics computes net subscribers correctly."""
        d = DailyAnalytics(
            date=datetime.now(),
            subscribers_gained=50,
            subscribers_lost=12,
        )
        assert d.net_subscribers == 38

    def test_channel_stats_creation(self):
        """ChannelStats model instantiates with required fields."""
        cs = ChannelStats(
            channel_id='UC_test',
            title='Test Channel',
            uploads_playlist_id='UU_test',
            published_at='2020-01-01T00:00:00Z',
        )
        assert cs.channel_id == 'UC_test'
        assert cs.subscriber_count == 0

    def test_video_analytics_defaults(self):
        """VideoAnalytics defaults numeric fields to 0."""
        va = VideoAnalytics(video_id='abc')
        assert va.views == 0
        assert va.engaged_views is None
        assert va.watch_time_minutes == 0.0
        assert va.subscribers_gained == 0

    def test_daily_analytics_engaged_views(self):
        """DailyAnalytics supports engaged_views metric."""
        d = DailyAnalytics(
            date=datetime.now(),
            views=1000,
            engaged_views=800,
        )
        assert d.engaged_views == 800

    def test_daily_analytics_engaged_views_optional(self):
        """engaged_views is None when not provided (pre-March 2025 data)."""
        d = DailyAnalytics(
            date=datetime.now(),
            views=1000,
        )
        assert d.engaged_views is None


# ---------------------------------------------------------------------------
# Database engagedViews tests
# ---------------------------------------------------------------------------

class TestDatabaseEngagedViews:
    """Tests for engaged_views and view_count_methodology in database."""

    @pytest.fixture
    def db(self, tmp_path):
        db_path = tmp_path / "test_analytics.db"
        return AnalyticsDatabase(db_path=db_path)

    def test_daily_stats_engaged_views(self, db):
        """engaged_views column persists in daily_stats."""
        from src.youtube_api.database import DailyStatsTable

        date = datetime(2025, 4, 1)
        db.add_daily_stats('vid_001', date, {
            'views': 1000,
            'engaged_views': 800,
            'watch_time_minutes': 50.0,
        })

        with db.get_session() as session:
            row = session.query(DailyStatsTable).filter_by(video_id='vid_001').first()
            assert row.engaged_views == 800

    def test_daily_stats_engaged_views_null(self, db):
        """engaged_views is NULL for pre-March 2025 data."""
        from src.youtube_api.database import DailyStatsTable

        date = datetime(2024, 12, 1)
        db.add_daily_stats('vid_001', date, {
            'views': 1000,
            'watch_time_minutes': 50.0,
        })

        with db.get_session() as session:
            row = session.query(DailyStatsTable).filter_by(video_id='vid_001').first()
            assert row.engaged_views is None

    def test_view_count_methodology(self, db):
        """view_count_methodology column persists in videos table."""
        video = {
            'video_id': 'v1',
            'title': 'Test | Show',
            'published_at': datetime(2025, 4, 1),
            'channel_id': 'UC_test',
            'channel_title': 'Test',
            'show_name': 'Show',
            'duration_minutes': 5.0,
            'is_short': False,
            'content_type': 'VIDEO_ON_DEMAND',
            'view_count_methodology': 'new_no_min_watch',
            'views': 500,
        }
        db.upsert_video(video)

        results = db.get_all_videos()
        assert results[0]['view_count_methodology'] == 'new_no_min_watch'


# ---------------------------------------------------------------------------
# Analytics API response parsing tests
# ---------------------------------------------------------------------------

class TestParseAnalyticsResponse:
    """Tests for _parse_analytics_response helper."""

    def test_parses_with_engaged_views(self):
        """Full response with engagedViews is parsed correctly."""
        response = {
            'columnHeaders': [
                {'name': 'day'},
                {'name': 'views'},
                {'name': 'engagedViews'},
                {'name': 'estimatedMinutesWatched'},
            ],
            'rows': [
                ['2025-04-01', 1000, 800, 50.5],
                ['2025-04-02', 1200, 950, 60.0],
            ]
        }
        parsed = _parse_analytics_response(response)

        assert len(parsed) == 2
        assert parsed[0]['day'] == '2025-04-01'
        assert parsed[0]['views'] == 1000
        assert parsed[0]['engagedViews'] == 800
        assert parsed[1]['estimatedMinutesWatched'] == 60.0

    def test_parses_without_engaged_views(self):
        """Pre-March 2025 response that omits engagedViews column."""
        response = {
            'columnHeaders': [
                {'name': 'day'},
                {'name': 'views'},
                {'name': 'estimatedMinutesWatched'},
            ],
            'rows': [
                ['2024-12-01', 500, 25.0],
            ]
        }
        parsed = _parse_analytics_response(response)

        assert len(parsed) == 1
        assert parsed[0]['views'] == 500
        assert 'engagedViews' not in parsed[0]
        # estimatedMinutesWatched is NOT shifted to wrong position
        assert parsed[0]['estimatedMinutesWatched'] == 25.0

    def test_empty_response(self):
        """Empty response returns empty list."""
        response = {'columnHeaders': [], 'rows': []}
        assert _parse_analytics_response(response) == []

    def test_no_rows(self):
        """Response with headers but no rows."""
        response = {
            'columnHeaders': [{'name': 'day'}, {'name': 'views'}],
        }
        assert _parse_analytics_response(response) == []


# ---------------------------------------------------------------------------
# Database migration tests
# ---------------------------------------------------------------------------

class TestDatabaseMigration:
    """Tests for backward-compatible schema migrations."""

    def test_migration_adds_missing_columns(self, tmp_path):
        """Opening a pre-existing DB adds content_type, view_count_methodology, engaged_views."""
        from sqlalchemy import create_engine, text

        db_path = tmp_path / "legacy.db"

        # Create a legacy schema WITHOUT the new columns
        legacy_engine = create_engine(f'sqlite:///{db_path}')
        with legacy_engine.connect() as conn:
            conn.execute(text("""
                CREATE TABLE videos (
                    video_id TEXT PRIMARY KEY,
                    title TEXT NOT NULL,
                    description TEXT,
                    published_at DATETIME NOT NULL,
                    channel_id TEXT NOT NULL,
                    channel_title TEXT,
                    show_name TEXT,
                    duration_minutes REAL,
                    is_short BOOLEAN DEFAULT 0,
                    views INTEGER DEFAULT 0,
                    likes INTEGER DEFAULT 0,
                    comments INTEGER DEFAULT 0,
                    engagement_rate REAL DEFAULT 0.0,
                    views_per_day REAL DEFAULT 0.0,
                    days_since_publication INTEGER DEFAULT 0,
                    last_updated DATETIME
                )
            """))
            conn.execute(text("""
                CREATE TABLE daily_stats (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    video_id TEXT NOT NULL,
                    date DATETIME NOT NULL,
                    views INTEGER DEFAULT 0,
                    likes INTEGER DEFAULT 0,
                    comments INTEGER DEFAULT 0,
                    watch_time_minutes REAL DEFAULT 0.0,
                    subscribers_gained INTEGER DEFAULT 0
                )
            """))
            conn.execute(text("""
                CREATE TABLE channel_snapshots (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    channel_id TEXT NOT NULL,
                    date DATETIME NOT NULL,
                    subscriber_count INTEGER DEFAULT 0,
                    video_count INTEGER DEFAULT 0,
                    view_count INTEGER DEFAULT 0,
                    daily_views INTEGER DEFAULT 0,
                    daily_watch_time_minutes REAL DEFAULT 0.0,
                    daily_subscribers_gained INTEGER DEFAULT 0,
                    daily_subscribers_lost INTEGER DEFAULT 0
                )
            """))
            conn.commit()
        legacy_engine.dispose()

        # Now open with AnalyticsDatabase — migration should add columns
        db = AnalyticsDatabase(db_path=db_path)

        # Verify we can write and read with the new columns
        db.upsert_video({
            'video_id': 'v1',
            'title': 'Test | Show',
            'published_at': datetime(2025, 1, 1),
            'channel_id': 'UC_test',
            'channel_title': 'Test',
            'show_name': 'Show',
            'duration_minutes': 5.0,
            'is_short': False,
            'content_type': 'VIDEO_ON_DEMAND',
            'view_count_methodology': 'new_no_min_watch',
            'views': 100,
        })

        results = db.get_all_videos()
        assert results[0]['content_type'] == 'VIDEO_ON_DEMAND'
        assert results[0]['view_count_methodology'] == 'new_no_min_watch'

        # Verify engaged_views works in daily_stats
        db.add_daily_stats('v1', datetime(2025, 4, 1), {
            'views': 50,
            'engaged_views': 40,
        })
        from src.youtube_api.database import DailyStatsTable
        with db.get_session() as session:
            row = session.query(DailyStatsTable).first()
            assert row.engaged_views == 40
