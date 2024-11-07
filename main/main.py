from fastapi.middleware.cors import CORSMiddleware
from fastapi import FastAPI, Depends, HTTPException, status, UploadFile, File
from pydantic import BaseModel
from typing import List, Optional
from enum import Enum
import enum
from sqlalchemy.orm import Session
from fastapi.security import OAuth2PasswordBearer
import jwt
from datetime import datetime, timedelta
import bcrypt
from .models import User
from .database import SessionLocal, engine, Base
from .schemas import RegisterRequest, LoginRequest, UserBase
from .crud import (
    login_user, register_user, logout_user, 
    get_user_profile, update_user_profile,
    import_sensor_data, get_dashboard_view,
    get_data_history
)

SECRET_KEY = "your_secret_key_here"
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30


def create_access_token(data: dict):
    # Crear una copia de los datos para evitar modificaciones
    to_encode = data.copy()

    # Añadir fecha de expiración
    expire = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode.update({"exp": expire})

    # Generar el token con la clave secreta y el algoritmo
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt

app = FastAPI()

# Configuración de CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=['*'],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Crear tablas en la base de datos
Base.metadata.create_all(bind=engine)

# Dependency para obtener la sesión de BD
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="login")
class GeneroEnum(str, Enum):
    MASCULINO = "MASCULINO"
    FEMENINO = "FEMENINO"

# Decodifica el token JWT para obtener los datos del usuario
def get_current_user(token: str = Depends(oauth2_scheme)):
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username = payload.get("sub")
        if username is None:
            raise HTTPException(status_code=401, detail="Invalid authentication credentials")
        return username
    except jwt.ExpiredSignatureError:
        raise HTTPException(status_code=401, detail="Token has expired")
    except jwt.InvalidTokenError:
        raise HTTPException(status_code=401, detail="Invalid token")

# Ruta de login
@app.post("/login")
async def login(request: LoginRequest, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.username == request.username).first()

    # Verifica si el usuario existe y la contraseña coincide
    if user is None or user.password != request.password:
        raise HTTPException(status_code=401, detail="Credenciales incorrectas")

    # Devolver el id del usuario si las credenciales son correctas
    return {"id": user.id}

@app.post("/register")
def register(request: RegisterRequest, db: Session = Depends(get_db)):
    try:
        gender = GeneroEnum[request.gender.upper()]  # Convierte a mayúsculas para evitar problemas de coincidencia
    except KeyError:
        raise HTTPException(status_code=400, detail=f"Invalid gender value: {request.gender}. Must be 'MASCULINO' or 'FEMENINO'.")
    
    return register_user(
        db=db,
        email=request.email,
        username=request.username,
        password=request.password,
        birthday=request.birthday,
        gender=gender,
        weight=request.weight,
        height=request.height
    )

@app.post("/logout", response_model=dict)
def logout(token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)):
    return {"message": "Logged out successfully."}

@app.get("/profile/{user_id}")
async def get_profile(user_id: int, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.id == user_id).first()  # Asegúrate de que solo uses `user_id`
    if not user:
        raise HTTPException(status_code=404, detail="Usuario no encontrado")
    return user



class UpdateProfileRequest(BaseModel):
    email: Optional[str]
    username: Optional[str]
    password: Optional[str]
    birthdate: Optional[str]
    gender: Optional[str]

@app.post("/profile/update", response_model=dict)
def update_profile(request: UpdateProfileRequest, db: Session = Depends(get_db), token: str = Depends(oauth2_scheme)):
    username = get_current_user(token)
    return update_user_profile(db, username, request)

@app.post("/import-data", response_model=dict)
def import_data(data_type: str, file: UploadFile = File(...), db: Session = Depends(get_db)):
    return import_sensor_data(db, data_type, file)

@app.get("/dashboard/view", response_model=dict)
def dashboard_view(db: Session = Depends(get_db), token: str = Depends(oauth2_scheme)):
    username = get_current_user(token)
    return get_dashboard_view(db, username)

@app.get("/dashboard/history", response_model=dict)
def data_history(user_id: int, data_type: str, period: str, db: Session = Depends(get_db)):
    return get_data_history(db, user_id, data_type, period)
