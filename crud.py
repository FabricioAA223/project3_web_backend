from sqlalchemy.orm import Session,joinedload
from sqlalchemy import desc
from . import models, schemas

# Crear un video
def create_video(db: Session, video: schemas.VideoCreate):
    db_video = models.Video(**video.model_dump())
    db.add(db_video)
    db.commit()
    db.refresh(db_video)
    return db_video

# Obtener un video por ID
def get_video(db: Session, video_id: int):
    return db.query(models.Video).filter(models.Video.id == video_id).first()

# Obtener todos los videos
def get_videos(db: Session, skip: int = 0, limit: int = 10):
    return db.query(models.Video).offset(skip).limit(limit).all()

# Crear un comentario
def create_comment(db: Session, comment: schemas.CommentCreate, video_id: int):
    db_comment = models.Comment(**comment.model_dump(), videoID=video_id)
    db.add(db_comment)
    db.commit()
    db.refresh(db_comment)
    return db_comment

# Marcar un video como favorito
def create_favorite_video(db: Session, video_id: int):
    db_favorite_video = models.FavoriteVideo(videoID=video_id)
    db.add(db_favorite_video)
    db.commit()
    db.refresh(db_favorite_video)
    return db_favorite_video

#Eliminar un video de favoritos
def delete_favorite_video(db: Session, id: int):
    item = db.query(models.FavoriteVideo).filter(models.FavoriteVideo.videoID == id).first()
    
    if item is None:
        return None

    db.delete(item)
    db.commit()
    return item

# Obtener los 10 videos con más vistas
def get_top_10_videos_by_views(db: Session):
    return db.query(models.Video).order_by(desc(models.Video.viewsCount)).limit(10).all()

# Obtener los 10 videos favoritos más recientes
def get_top_10_recent_favorite_videos(db: Session):
    response = (
        db.query(models.Video)
        .join(models.FavoriteVideo, models.Video.id == models.FavoriteVideo.videoID)
        .order_by(desc(models.FavoriteVideo.favoriteDate))
        .limit(10)
        .all()
    )
    return response

# Buscar videos por título o descripción
def search_videos(db: Session, query: str):
    return db.query(models.Video).options(
        joinedload(models.Video.isFavorite),  #load the isFavorite relationship
    ).filter(
        (models.Video.title.ilike(f'%{query}%')) | 
        (models.Video.description.ilike(f'%{query}%'))
    ).all()

# Incrementar el número de reproducciones de un video
def increment_video_views(db: Session, video_id: int):
    db_video = db.query(models.Video).filter(models.Video.id == video_id).first()
    if db_video:
        db_video.viewsCount += 1
        db.commit()
        db.refresh(db_video)
    return db_video
