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
            ('daily_stats', 'engaged_views', 'INTEGER'),
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

    def get_show_summary(self) -> List[Dict[str, Any]]:
        """
        Get aggregated stats by show.

        Returns:
            List of show summary dicts
        """
        with self.get_session() as session:
            results = session.query(
                VideoTable.show_name,
                func.count(VideoTable.video_id).label('video_count'),
                func.sum(VideoTable.views).label('total_views'),
                func.sum(VideoTable.likes).label('total_likes'),
                func.avg(VideoTable.engagement_rate).label('avg_engagement'),
                func.sum(VideoTable.is_short.cast(Integer)).label('shorts_count')
            ).group_by(VideoTable.show_name).order_by(
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

    def get_shorts_vs_longform(self) -> Dict[str, Any]:
        """
        Get comparative stats for Shorts vs longform.

        Returns:
            Dict with comparative metrics
        """
        with self.get_session() as session:
            shorts = session.query(
                func.count(VideoTable.video_id).label('count'),
                func.sum(VideoTable.views).label('views'),
                func.avg(VideoTable.views).label('avg_views'),
                func.avg(VideoTable.engagement_rate).label('avg_engagement')
            ).filter(VideoTable.is_short == True).first()

            longform = session.query(
                func.count(VideoTable.video_id).label('count'),
                func.sum(VideoTable.views).label('views'),
                func.avg(VideoTable.views).label('avg_views'),
                func.avg(VideoTable.engagement_rate).label('avg_engagement')
            ).filter(VideoTable.is_short == False).first()

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
