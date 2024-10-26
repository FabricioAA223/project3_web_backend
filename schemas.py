from pydantic import BaseModel
from datetime import datetime
from typing import List, Optional

class CommentBase(BaseModel):
    comment: str

class CommentCreate(CommentBase):
    pass

class Comment(CommentBase):
    id: int
    videoID: int
    creationDate: datetime

    class Config:
        orm_mode = True

class FavoriteVideoBase(BaseModel):
    favoriteDate: datetime

class FavoriteVideoCreate(FavoriteVideoBase):
    pass

class FavoriteVideo(FavoriteVideoBase):
    id: int
    videoID: int

    class Config:
        orm_mode = True

class VideoBase(BaseModel):
    title: str
    description: Optional[str] = None
    videoPath: str
    thumbnailPath: str

class VideoCreate(VideoBase):
    pass

class Video(VideoBase):
    id: int
    creationDate: datetime
    viewsCount: int
    isFavorite: Optional[FavoriteVideo]
    comments: List[Comment] = []

    class Config:
        orm_mode = True