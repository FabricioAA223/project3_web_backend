import os
import shutil
import uuid
from fastapi import FastAPI, Depends, File, Form, HTTPException, UploadFile
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
from . import crud, models, schemas
from .database import SessionLocal, engine, Base
from fastapi.staticfiles import StaticFiles

Base.metadata.create_all(bind=engine)

app = FastAPI()

origins = ['*']

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Crear un directorio para almacenar los archivos si no existe
os.makedirs('uploaded_videos', exist_ok=True)
os.makedirs('thumbnails', exist_ok=True)

# Montar la carpeta de videos en la ruta "/uploaded_videos"
app.mount("/uploaded_videos", StaticFiles(directory="uploaded_videos"), name="uploaded_videos")
app.mount("/thumbnails", StaticFiles(directory="thumbnails"), name="thumbnails")
video_directory = "uploaded_videos"
thumbnail_directory = "thumbnails"

# Dependencia para obtener la sesión de la base de datos
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@app.post("/videos/", response_model=schemas.Video)
def create_video(
    title: str = Form(...),
    description: str | None = Form(None),
    videoFile: UploadFile = File(...),
    thumbnailFile: UploadFile | None = File(None),  # Es opcional
    db: Session = Depends(get_db)
):
    # Generar un ID único para los archivos
    video_id = str(uuid.uuid4())
    
    # Definir las rutas de los archivos
    video_filename = f"{video_id}.mp4"
    videoPath = os.path.join("uploaded_videos", video_filename)
    
    if thumbnailFile:
        thumbnail_filename = f"{video_id}.jpg"
        thumbnailPath = os.path.join("thumbnails", thumbnail_filename)
    else:
        thumbnailPath = "thumbnails\\default_thumbnail.png"  # Ruta de la imagen predeterminada
    
    try:
        # Guardar el video en la carpeta correspondiente
        with open(videoPath, "wb") as buffer:
            shutil.copyfileobj(videoFile.file, buffer)
        
        # Guardar el thumbnail si se proporciona
        if thumbnailFile:
            with open(thumbnailPath, "wb") as buffer:
                shutil.copyfileobj(thumbnailFile.file, buffer)
        
        # Construir el objeto VideoCreate para guardar en la base de datos
        video_data = schemas.VideoCreate(
            title=title,
            description=description,
            videoPath=f"/{video_directory}/{video_filename}",
            thumbnailPath=f"/{thumbnail_directory}/{thumbnail_filename}" if thumbnailFile else f"/{thumbnail_directory}/default_thumbnail.png"
        )
        
        # Guardar la información del video en la base de datos
        return crud.create_video(db=db, video=video_data)
    
    except Exception as e:
        # Si ocurre algún error, eliminar los archivos guardados
        if os.path.exists(videoPath):
            os.remove(videoPath)
        
        if thumbnailFile and os.path.exists(thumbnailPath):
            os.remove(thumbnailPath)

        # Lanzar el error nuevamente para que sea manejado por FastAPI
        raise HTTPException(status_code=500, detail=f"Error al guardar el video: {str(e)}")


@app.get("/videos/{video_id}", response_model=schemas.Video)
def read_video(video_id: int, db: Session = Depends(get_db)):
    db_video = crud.get_video(db=db, video_id=video_id)
    if db_video is None:
        raise HTTPException(status_code=404, detail="Video not found")
    return db_video

@app.get("/videos/", response_model=list[schemas.Video])
def read_videos(skip: int = 0, limit: int = 10, db: Session = Depends(get_db)):
    videos = crud.get_videos(db=db, skip=skip, limit=limit)
    return videos

 
@app.post("/videos/{video_id}/favorites/")
def create_favorite(video_id: int, db: Session = Depends(get_db)):
    return crud.create_favorite_video(db=db, video_id=video_id)

@app.delete("/videos/{video_id}/favorites/")
def delete_favorite(video_id: int, db: Session = Depends(get_db)):
    item = crud.delete_favorite_video(db=db, id=video_id)
    if item is None:
        raise HTTPException(status_code=404, detail="Favorite item not found")
    return {"detail": "Favorite item deleted"}

@app.get("/videos/top/views/", response_model=list[schemas.Video])
def read_top_videos(db: Session = Depends(get_db)):
    return crud.get_top_10_videos_by_views(db=db)

@app.get("/videos/top/favorites/", response_model=list[schemas.Video])
def read_top_favorite_videos(db: Session = Depends(get_db)):
    return crud.get_top_10_recent_favorite_videos(db=db)

@app.get("/videos/search/")
def search_videos(query: str, db: Session = Depends(get_db)):
    return crud.search_videos(db=db, query=query)

@app.put("/videos/{video_id}/increment_views/")
def increment_views(video_id: int, db: Session = Depends(get_db)):
    return crud.increment_video_views(db=db, video_id=video_id)

@app.post("/videos/{video_id}/comments/", response_model=schemas.Comment)
def create_comment_for_video(video_id: int, comment: schemas.CommentCreate = Form(...), db: Session = Depends(get_db)):
    return crud.create_comment(db=db, comment=comment, video_id=video_id)