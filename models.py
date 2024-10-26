from sqlalchemy import Boolean, Column, ForeignKey, Integer, String, DateTime
from sqlalchemy.orm import relationship
from datetime import datetime, timezone
from .database import Base


class Video(Base):
    __tablename__ = "videos"

    #Atributos de la tabla
    id = Column(Integer, primary_key=True, index=True)
    title = Column(String, index=True, nullable=False)
    creationDate = Column(DateTime, default=lambda: datetime.now(timezone.utc))
    description = Column(String, index=True)
    videoPath = Column(String, nullable=False)
    thumbnailPath = Column(String, nullable=False)
    viewsCount = Column(Integer, default=0)

    isFavorite = relationship("FavoriteVideo", back_populates="video", uselist=False, cascade="all, delete")
    comments = relationship("Comment", back_populates="video", cascade="all, delete")

class FavoriteVideo(Base):
    __tablename__ = 'favorite_videos'

    id = Column(Integer, primary_key=True, index=True)
    videoID = Column(Integer, ForeignKey('videos.id'), nullable=False)
    favoriteDate = Column(DateTime, default=lambda: datetime.now(timezone.utc))

    video = relationship("Video", back_populates="isFavorite")

class Comment(Base):
    __tablename__ = 'comments'

    id = Column(Integer, primary_key=True, index=True)
    videoID = Column(Integer, ForeignKey('videos.id'), nullable=False)
    comment = Column(String, nullable=False)
    creationDate = Column(DateTime, default=datetime.now(timezone.utc))

    video = relationship("Video", back_populates="comments")