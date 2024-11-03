from fastapi.middleware.cors import CORSMiddleware
from fastapi import FastAPI, Depends, HTTPException, status, UploadFile, File
from pydantic import BaseModel
from typing import List, Optional
from enum import Enum
import enum
from sqlalchemy.orm import Session
from fastapi.security import OAuth2PasswordBearer
import jwt
from .database import SessionLocal, engine, Base
from .exampleData import exampleData
from .schemas import RegisterRequest
from .crud import (
    login_user, register_user, logout_user, 
    get_user_profile, update_user_profile,
    import_sensor_data, get_dashboard_view,
    get_data_history
)

SECRET_KEY = "your_secret_key_here"
ALGORITHM = "HS256"

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

# Cargar datos de ejemplo solo una vez
with SessionLocal() as db:
    exampleData(db)
# Dependency para obtener la sesión de BD

class GeneroEnum(enum.Enum):
    MASCULINO = "Masculino"
    FEMENINO = "Femenino"

# Dependency para obtener la sesión de BD
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

class LoginRequest(BaseModel):
    username: str
    password: str

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="login")

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

# Rutas de la API
@app.post("/login", response_model=dict)
def login(request: LoginRequest, db: Session = Depends(get_db)):
    return login_user(db, request.username, request.password)

@app.post("/register")
def register(request: RegisterRequest, db: Session = Depends(get_db)):
    gender = GeneroEnum[request.gender.upper()]  # Conviértelo a mayúsculas si es necesario
    # Llama a register_user con el password incluido
    return register_user(db, request.email, request.username, request.password, request.birthday, request.gender)


@app.post("/logout", response_model=dict)
def logout(token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)):
    # Aquí podrías implementar la lógica de cierre de sesión si es necesario.
    return {"message": "Logged out successfully."}

@app.get("/profile", response_model=dict)
def get_profile(db: Session = Depends(get_db), token: str = Depends(oauth2_scheme)):
    username = get_current_user(token)
    return get_user_profile(db, username)

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
