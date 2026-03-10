"""
SQLite Database Module for YouTube Analytics.
Provides local data persistence for historical trend analysis.
"""

import logging
from datetime import datetime
from pathlib import Path
from typing import Optional, List, Dict, Any

from sqlalchemy import create_engine, Column, String, Integer, Float, Boolean, DateTime, Index, text, inspect
from sqlalchemy.orm import declarative_base, sessionmaker, Session
from sqlalchemy.sql import func

logger = logging.getLogger(__name__)

Base = declarative_base()

# Default database path
DEFAULT_DB_PATH = Path(__file__).parent.parent.parent / 'data' / 'youtube_analytics.db'


class VideoTable(Base):
    """SQLAlchemy model for videos table."""
    __tablename__ = 'videos'

    video_id = Column(String, primary_key=True)
    title = Column(String, nullable=False)
    description = Column(String)
    published_at = Column(DateTime, nullable=False)
    channel_id = Column(String, nullable=False)
    channel_title = Column(String)
    show_name = Column(String)
    duration_minutes = Column(Float)
    is_short = Column(Boolean, default=False)
    content_type = Column(String, default='UNSPECIFIED')
    view_count_methodology = Column(String, default='legacy')
    views = Column(Integer, default=0)
    likes = Column(Integer, default=0)
    comments = Column(Integer, default=0)
    engagement_rate = Column(Float, default=0.0)
    avg_view_pct = Column(Float, default=0.0)
    ctr = Column(Float, default=0.0)
    viewed_vs_swiped_pct = Column(Float, default=0.0)
    views_per_day = Column(Float, default=0.0)
    days_since_publication = Column(Integer, default=0)
    last_updated = Column(DateTime, default=func.now(), onupdate=func.now())

    # Indexes for common queries
    __table_args__ = (
        Index('idx_videos_channel', 'channel_id'),
        Index('idx_videos_show', 'show_name'),
        Index('idx_videos_published', 'published_at'),
        Index('idx_videos_is_short', 'is_short'),
        Index('idx_videos_content_type', 'content_type'),
    )


class DailyStatsTable(Base):
    """SQLAlchemy model for daily video statistics."""
    __tablename__ = 'daily_stats'

    id = Column(Integer, primary_key=True, autoincrement=True)
    video_id = Column(String, nullable=False)
    date = Column(DateTime, nullable=False)
    views = Column(Integer, default=0)
    engaged_views = Column(Integer, nullable=True)
    likes = Column(Integer, default=0)
    comments = Column(Integer, default=0)
    watch_time_minutes = Column(Float, default=0.0)
    avg_view_pct = Column(Float, default=0.0)
    ctr = Column(Float, default=0.0)
    viewed_vs_swiped_pct = Column(Float, default=0.0)
    subscribers_gained = Column(Integer, default=0)

    __table_args__ = (
        Index('idx_daily_video_date', 'video_id', 'date', unique=True),
        Index('idx_daily_date', 'date'),
    )


class ChannelSnapshotTable(Base):
    """SQLAlchemy model for daily channel snapshots."""
    __tablename__ = 'channel_snapshots'

    id = Column(Integer, primary_key=True, autoincrement=True)
    channel_id = Column(String, nullable=False)
    date = Column(DateTime, nullable=False)
    subscriber_count = Column(Integer, default=0)
    video_count = Column(Integer, default=0)
    view_count = Column(Integer, default=0)
    daily_views = Column(Integer, default=0)
    daily_watch_time_minutes = Column(Float, default=0.0)
    avg_view_pct = Column(Float, default=0.0)
    ctr = Column(Float, default=0.0)
    viewed_vs_swiped_pct = Column(Float, default=0.0)
    daily_subscribers_gained = Column(Integer, default=0)
    daily_subscribers_lost = Column(Integer, default=0)

    __table_args__ = (
        Index('idx_snapshot_channel_date', 'channel_id', 'date', unique=True),
        Index('idx_snapshot_date', 'date'),
    )


class AnalyticsDatabase:
    """
    Database interface for YouTube analytics data.
    """

    def __init__(self, db_path: Optional[Path] = None):
        """
        Initialize database connection.

        Args:
            db_path: Path to SQLite database file
        """
        self.db_path = db_path or DEFAULT_DB_PATH
        self.db_path.parent.mkdir(parents=True, exist_ok=True)

        self.engine = create_engine(f'sqlite:///{self.db_path}', echo=False)
        self.SessionLocal = sessionmaker(bind=self.engine)

        # Create tables if they don't exist
        Base.metadata.create_all(self.engine)

        # Migrate existing tables (add columns that may be missing)
        self._migrate_schema()

        logger.info(f"Database initialized at {self.db_path}")

    def _migrate_schema(self) -> None:
        """Add columns introduced after initial schema creation.

        SQLAlchemy's create_all() only creates new tables — it does not alter
        existing ones. This method handles backward-compatible ALTER TABLE
        additions for existing SQLite databases.
        """
        migrations = [
            ('videos', 'content_type', "TEXT DEFAULT 'UNSPECIFIED'"),
            ('videos', 'view_count_methodology', "TEXT DEFAULT 'legacy'"),
            ('videos', 'avg_view_pct', "FLOAT DEFAULT 0.0"),
            ('videos', 'ctr', "FLOAT DEFAULT 0.0"),
            ('videos', 'viewed_vs_swiped_pct', "FLOAT DEFAULT 0.0"),
            ('daily_stats', 'engaged_views', 'INTEGER'),
            ('daily_stats', 'avg_view_pct', "FLOAT DEFAULT 0.0"),
            ('daily_stats', 'ctr', "FLOAT DEFAULT 0.0"),
            ('daily_stats', 'viewed_vs_swiped_pct', "FLOAT DEFAULT 0.0"),
            ('channel_snapshots', 'avg_view_pct', "FLOAT DEFAULT 0.0"),
            ('channel_snapshots', 'ctr', "FLOAT DEFAULT 0.0"),
            ('channel_snapshots', 'viewed_vs_swiped_pct', "FLOAT DEFAULT 0.0"),
        ]

        with self.engine.connect() as conn:
            inspector = inspect(self.engine)
            for table_name, column_name, col_type in migrations:
                existing_cols = {
                    c['name'] for c in inspector.get_columns(table_name)
                }
                if column_name not in existing_cols:
                    conn.execute(text(
                        f'ALTER TABLE {table_name} ADD COLUMN {column_name} {col_type}'
                    ))
                    conn.commit()
                    logger.info(f"Migrated: added {column_name} to {table_name}")

    def get_session(self) -> Session:
        """Get a new database session."""
        return self.SessionLocal()

    def upsert_video(self, video_data: Dict[str, Any]) -> None:
        """
        Insert or update a video record.

        Args:
            video_data: Dictionary with video fields
        """
        with self.get_session() as session:
            existing = session.query(VideoTable).filter_by(
                video_id=video_data['video_id']
            ).first()

            if existing:
                for key, value in video_data.items():
                    if hasattr(existing, key):
                        setattr(existing, key, value)
            else:
                video = VideoTable(**video_data)
                session.add(video)

            session.commit()

    def upsert_videos_bulk(self, videos: List[Dict[str, Any]]) -> int:
        """
        Bulk insert or update video records.

        Args:
            videos: List of video data dicts

        Returns:
            Number of records processed
        """
        with self.get_session() as session:
            for video_data in videos:
                existing = session.query(VideoTable).filter_by(
                    video_id=video_data['video_id']
                ).first()

                if existing:
                    for key, value in video_data.items():
                        if hasattr(existing, key):
                            setattr(existing, key, value)
                else:
                    video = VideoTable(**video_data)
                    session.add(video)

            session.commit()

        logger.info(f"Upserted {len(videos)} video records")
        return len(videos)

    def add_daily_stats(self, video_id: str, date: datetime, stats: Dict[str, Any]) -> None:
        """
        Add daily stats snapshot for a video.

        Args:
            video_id: YouTube video ID
            date: Date of the snapshot
            stats: Stats dictionary
        """
        with self.get_session() as session:
            # Check if exists
            existing = session.query(DailyStatsTable).filter_by(
                video_id=video_id,
                date=date
            ).first()

            if existing:
                for key, value in stats.items():
                    if hasattr(existing, key):
                        setattr(existing, key, value)
            else:
                record = DailyStatsTable(
                    video_id=video_id,
                    date=date,
                    **stats
                )
                session.add(record)

            session.commit()

    def add_channel_snapshot(self, channel_id: str, date: datetime, stats: Dict[str, Any]) -> None:
        """
        Add daily channel snapshot.

        Args:
            channel_id: YouTube channel ID
            date: Date of the snapshot
            stats: Stats dictionary
        """
        with self.get_session() as session:
            existing = session.query(ChannelSnapshotTable).filter_by(
                channel_id=channel_id,
                date=date
            ).first()

            if existing:
                for key, value in stats.items():
                    if hasattr(existing, key):
                        setattr(existing, key, value)
            else:
                record = ChannelSnapshotTable(
                    channel_id=channel_id,
                    date=date,
                    **stats
                )
                session.add(record)

            session.commit()

    def get_all_videos(self, channel_id: Optional[str] = None) -> List[Dict[str, Any]]:
        """
        Get all videos, optionally filtered by channel.

        Args:
            channel_id: Optional channel ID filter

        Returns:
            List of video dicts
        """
        with self.get_session() as session:
            query = session.query(VideoTable)
            if channel_id:
                query = query.filter_by(channel_id=channel_id)

            videos = query.order_by(VideoTable.published_at.desc()).all()

            return [
                {c.name: getattr(v, c.name) for c in VideoTable.__table__.columns}
                for v in videos
            ]

    def get_archival_videos(
        self,
        months_threshold: int = 12,
        channel_id: Optional[str] = None
    ) -> List[Dict[str, Any]]:
        """
        Get videos older than threshold.

        Args:
            months_threshold: Age threshold in months
            channel_id: Optional channel filter

        Returns:
            List of archival video dicts
        """
        from datetime import timedelta
        cutoff = datetime.now() - timedelta(days=months_threshold * 30)

        with self.get_session() as session:
            query = session.query(VideoTable).filter(
                VideoTable.published_at < cutoff
            )

            if channel_id:
                query = query.filter_by(channel_id=channel_id)

            videos = query.order_by(VideoTable.views_per_day.desc()).all()

            return [
                {c.name: getattr(v, c.name) for c in VideoTable.__table__.columns}
                for v in videos
            ]

    def get_show_summary(self, channel_id: Optional[str] = None) -> List[Dict[str, Any]]:
        """
        Get aggregated stats by show.

        Args:
            channel_id: Optional channel filter

        Returns:
            List of show summary dicts
        """
        with self.get_session() as session:
            query = session.query(
                VideoTable.show_name,
                func.count(VideoTable.video_id).label('video_count'),
                func.sum(VideoTable.views).label('total_views'),
                func.sum(VideoTable.likes).label('total_likes'),
                func.avg(VideoTable.engagement_rate).label('avg_engagement'),
                func.sum(VideoTable.is_short.cast(Integer)).label('shorts_count')
            )
            if channel_id:
                query = query.filter(VideoTable.channel_id == channel_id)
            results = query.group_by(VideoTable.show_name).order_by(
                func.sum(VideoTable.views).desc()
            ).all()

            return [
                {
                    'show_name': r.show_name,
                    'video_count': r.video_count,
                    'total_views': r.total_views or 0,
                    'total_likes': r.total_likes or 0,
                    'avg_engagement': r.avg_engagement or 0.0,
                    'shorts_count': r.shorts_count or 0
                }
                for r in results
            ]

    def get_shorts_vs_longform(self, channel_id: Optional[str] = None) -> Dict[str, Any]:
        """
        Get comparative stats for Shorts vs longform.

        Args:
            channel_id: Optional channel filter

        Returns:
            Dict with comparative metrics
        """
        with self.get_session() as session:
            shorts_q = session.query(
                func.count(VideoTable.video_id).label('count'),
                func.sum(VideoTable.views).label('views'),
                func.avg(VideoTable.views).label('avg_views'),
                func.avg(VideoTable.engagement_rate).label('avg_engagement')
            ).filter(VideoTable.is_short == True)
            if channel_id:
                shorts_q = shorts_q.filter(VideoTable.channel_id == channel_id)
            shorts = shorts_q.first()

            longform_q = session.query(
                func.count(VideoTable.video_id).label('count'),
                func.sum(VideoTable.views).label('views'),
                func.avg(VideoTable.views).label('avg_views'),
                func.avg(VideoTable.engagement_rate).label('avg_engagement')
            ).filter(VideoTable.is_short == False)
            if channel_id:
                longform_q = longform_q.filter(VideoTable.channel_id == channel_id)
            longform = longform_q.first()

            return {
                'shorts': {
                    'count': shorts.count or 0,
                    'total_views': shorts.views or 0,
                    'avg_views': shorts.avg_views or 0.0,
                    'avg_engagement': shorts.avg_engagement or 0.0
                },
                'longform': {
                    'count': longform.count or 0,
                    'total_views': longform.views or 0,
                    'avg_views': longform.avg_views or 0.0,
                    'avg_engagement': longform.avg_engagement or 0.0
                }
            }

    def get_shorts_detail(self, channel_id: Optional[str] = None) -> List[Dict[str, Any]]:
        """
        Get all Shorts videos ordered by views descending.

        Args:
            channel_id: Optional channel filter

        Returns:
            List of video dicts for Shorts
        """
        with self.get_session() as session:
            query = session.query(VideoTable).filter(VideoTable.is_short == True)
            if channel_id:
                query = query.filter(VideoTable.channel_id == channel_id)
            videos = query.order_by(VideoTable.views.desc()).all()
            return [
                {c.name: getattr(v, c.name) for c in VideoTable.__table__.columns}
                for v in videos
            ]

    def get_video_daily_stats(self, video_id: str, days: int = 28) -> List[Dict[str, Any]]:
        """
        Get daily stats for a specific video.

        Args:
            video_id: YouTube video ID
            days: Number of most recent days to return

        Returns:
            List of daily stat dicts ordered by date ASC
        """
        from datetime import timedelta
        cutoff = datetime.now() - timedelta(days=days)

        with self.get_session() as session:
            rows = session.query(DailyStatsTable).filter(
                DailyStatsTable.video_id == video_id,
                DailyStatsTable.date >= cutoff
            ).order_by(DailyStatsTable.date.asc()).all()

            return [
                {
                    'date': r.date,
                    'views': r.views,
                    'engaged_views': r.engaged_views,
                    'watch_time_minutes': r.watch_time_minutes,
                    'avg_view_pct': r.avg_view_pct or 0.0,
                    'ctr': r.ctr or 0.0,
                    'viewed_vs_swiped_pct': r.viewed_vs_swiped_pct or 0.0,
                    'subscribers_gained': r.subscribers_gained,
                    'likes': r.likes,
                    'comments': r.comments,
                }
                for r in rows
            ]

    def get_shorts_daily_aggregate(
        self,
        channel_id: Optional[str] = None,
        days: int = 90
    ) -> List[Dict[str, Any]]:
        """
        Get daily aggregated stats for all Shorts.

        Args:
            channel_id: Optional channel filter
            days: Number of most recent days to return

        Returns:
            List of daily aggregate dicts ordered by date ASC
        """
        from datetime import timedelta
        cutoff = datetime.now() - timedelta(days=days)

        with self.get_session() as session:
            query = session.query(
                DailyStatsTable.date,
                func.sum(DailyStatsTable.views).label('views'),
                func.sum(DailyStatsTable.engaged_views).label('engaged_views'),
                func.sum(DailyStatsTable.watch_time_minutes).label('watch_time_minutes'),
                func.avg(DailyStatsTable.avg_view_pct).label('avg_view_pct'),
                func.avg(DailyStatsTable.ctr).label('ctr'),
                func.avg(DailyStatsTable.viewed_vs_swiped_pct).label('viewed_vs_swiped_pct'),
                func.sum(DailyStatsTable.subscribers_gained).label('subscribers_gained'),
            ).join(
                VideoTable,
                DailyStatsTable.video_id == VideoTable.video_id
            ).filter(
                VideoTable.is_short == True,
                DailyStatsTable.date >= cutoff
            )

            if channel_id:
                query = query.filter(VideoTable.channel_id == channel_id)

            rows = query.group_by(DailyStatsTable.date).order_by(
                DailyStatsTable.date.asc()
            ).all()

            return [
                {
                    'date': r.date,
                    'views': r.views or 0,
                    'engaged_views': r.engaged_views,
                    'watch_time_minutes': r.watch_time_minutes or 0.0,
                    'avg_view_pct': r.avg_view_pct or 0.0,
                    'ctr': r.ctr or 0.0,
                    'viewed_vs_swiped_pct': r.viewed_vs_swiped_pct or 0.0,
                    'subscribers_gained': r.subscribers_gained or 0,
                }
                for r in rows
            ]

    def get_channel_history(
        self,
        channel_id: str,
        days: int = 90
    ) -> List[Dict[str, Any]]:
        """
        Get historical channel snapshots.

        Args:
            channel_id: Channel ID
            days: Number of days of history

        Returns:
            List of daily snapshot dicts
        """
        from datetime import timedelta
        cutoff = datetime.now() - timedelta(days=days)

        with self.get_session() as session:
            snapshots = session.query(ChannelSnapshotTable).filter(
                ChannelSnapshotTable.channel_id == channel_id,
                ChannelSnapshotTable.date >= cutoff
            ).order_by(ChannelSnapshotTable.date).all()

            return [
                {c.name: getattr(s, c.name) for c in ChannelSnapshotTable.__table__.columns}
                for s in snapshots
            ]

    def get_show_stats_for_scoring(self, channel_id: Optional[str] = None) -> Dict[str, Dict[str, float]]:
        """Get per-show mean and stddev of views_per_day for z-score computation.

        Returns:
            Dict mapping show_name -> {'mean': float, 'stddev': float, 'count': int}
        """
        with self.get_session() as session:
            query = session.query(
                VideoTable.show_name,
                func.avg(VideoTable.views_per_day).label('mean'),
                func.count(VideoTable.video_id).label('count'),
            )
            if channel_id:
                query = query.filter(VideoTable.channel_id == channel_id)
            results = query.group_by(VideoTable.show_name).all()

            stats = {}
            for r in results:
                show = r.show_name or "Uncategorized"
                mean = r.mean or 0.0
                count = r.count or 0

                # Compute stddev in a second query (SQLite has no built-in stddev)
                sq = session.query(
                    func.avg((VideoTable.views_per_day - mean) * (VideoTable.views_per_day - mean))
                ).filter(VideoTable.show_name == r.show_name)
                if channel_id:
                    sq = sq.filter(VideoTable.channel_id == channel_id)
                variance = sq.scalar() or 0.0

                stats[show] = {
                    'mean': round(mean, 4),
                    'stddev': round(variance ** 0.5, 4),
                    'count': count,
                }
            return stats

    def get_videos_with_show_context(
        self,
        channel_id: Optional[str] = None,
        published_after: Optional[datetime] = None,
    ) -> List[Dict[str, Any]]:
        """Get all videos with show-relative performance context.

        Args:
            channel_id: Optional channel filter
            published_after: Optional date filter for recent content

        Returns:
            List of video dicts with added fields: show_avg_vpd, show_stddev_vpd,
            z_score, vs_show_multiplier
        """
        show_stats = self.get_show_stats_for_scoring(channel_id=channel_id)
        videos = self.get_all_videos(channel_id=channel_id)

        enriched = []
        for v in videos:
            if published_after and v.get("published_at"):
                if v["published_at"] < published_after:
                    continue

            show = v.get("show_name") or "Uncategorized"
            ss = show_stats.get(show, {"mean": 0, "stddev": 0, "count": 0})
            vpd = v.get("views_per_day", 0) or 0
            mean = ss["mean"]
            stddev = ss["stddev"]

            z_score = (vpd - mean) / stddev if stddev > 0 else 0.0
            multiplier = vpd / mean if mean > 0 else 0.0

            v["show_avg_vpd"] = round(mean, 2)
            v["show_stddev_vpd"] = round(stddev, 2)
            v["z_score"] = round(z_score, 2)
            v["vs_show_multiplier"] = round(multiplier, 2)
            enriched.append(v)

        return enriched

    def get_show_variance_analysis(self, channel_id: Optional[str] = None) -> List[Dict[str, Any]]:
        """Get shows ranked by coefficient of variation (stddev/mean of views_per_day).

        High CoV = inconsistent show where topic/title matters more than brand.

        Returns:
            List of show dicts with mean, stddev, coeff_of_variation, hit_rate
        """
        show_stats = self.get_show_stats_for_scoring(channel_id=channel_id)
        results = []
        for show_name, ss in show_stats.items():
            if ss["count"] < 5:  # skip shows with too few videos for meaningful stats
                continue
            mean = ss["mean"]
            stddev = ss["stddev"]
            cov = stddev / mean if mean > 0 else 0.0

            # Count hits (>2 sigma)
            hit_threshold = mean + 2 * stddev
            with self.get_session() as session:
                query = session.query(func.count(VideoTable.video_id)).filter(
                    VideoTable.show_name == show_name,
                    VideoTable.views_per_day > hit_threshold,
                )
                if channel_id:
                    query = query.filter(VideoTable.channel_id == channel_id)
                hit_count = query.scalar() or 0

            results.append({
                "show_name": show_name,
                "video_count": ss["count"],
                "avg_views_per_day": round(mean, 2),
                "stddev_views_per_day": round(stddev, 2),
                "coeff_of_variation": round(cov, 2),
                "hit_count": hit_count,
                "hit_rate": round(hit_count / ss["count"] * 100, 1) if ss["count"] > 0 else 0.0,
            })

        results.sort(key=lambda x: x["coeff_of_variation"], reverse=True)
        return results

    def get_format_gaps(self, channel_id: Optional[str] = None) -> Dict[str, List[Dict[str, Any]]]:
        """Identify shows with format opportunities.

        Returns:
            Dict with 'no_shorts' (longform shows with 0 Shorts) and
            'underperforming' (shows with below-average and declining views/day)
        """
        shows = self.get_show_summary(channel_id=channel_id)
        all_videos = self.get_all_videos(channel_id=channel_id)

        # Channel average views_per_day
        channel_avg_vpd = 0.0
        if all_videos:
            channel_avg_vpd = sum(v.get("views_per_day", 0) or 0 for v in all_videos) / len(all_videos)

        no_shorts = []
        underperforming = []

        for show in shows:
            name = show.get("show_name")
            count = show.get("video_count", 0)
            shorts = show.get("shorts_count", 0)

            if count >= 5 and shorts == 0:
                no_shorts.append({
                    "show_name": name,
                    "video_count": count,
                    "total_views": show.get("total_views", 0),
                    "avg_engagement": round(show.get("avg_engagement", 0), 2),
                })

            if count >= 5:
                # Compute show avg views/day
                show_vpd = sum(
                    v.get("views_per_day", 0) or 0
                    for v in all_videos
                    if v.get("show_name") == name
                ) / max(count, 1)

                if show_vpd < channel_avg_vpd * 0.7:
                    underperforming.append({
                        "show_name": name,
                        "video_count": count,
                        "avg_views_per_day": round(show_vpd, 2),
                        "channel_avg_views_per_day": round(channel_avg_vpd, 2),
                        "ratio": round(show_vpd / channel_avg_vpd, 2) if channel_avg_vpd > 0 else 0,
                    })

        no_shorts.sort(key=lambda x: x["video_count"], reverse=True)
        underperforming.sort(key=lambda x: x["avg_views_per_day"])

        return {"no_shorts": no_shorts, "underperforming": underperforming}
