from fastapi.middleware.cors import CORSMiddleware
from fastapi import FastAPI, Depends, HTTPException, status, UploadFile, File
from pydantic import BaseModel
from fastapi.security import OAuth2PasswordBearer
from typing import List, Optional
from sqlalchemy.orm import Session
from .database import SessionLocal, engine, Base
from .crud import (
    login_user, register_user, logout_user, 
    get_user_profile, update_user_profile,
    import_sensor_data, get_dashboard_view,
    get_data_history, add_dummy_user, get_current_user
)
# Definir oauth2_scheme
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="login")
app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=['*'],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Conexión a la base de datos
Base.metadata.create_all(bind=engine)

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

@app.post("/login")
def login(request: LoginRequest, db: Session = Depends(get_db)):
    return login_user(db, request.username, request.password)

class RegisterRequest(BaseModel):
    email: str
    username: str
    password: str
    weight: float
    height: float
    birthdate: str
    gender: str

# Modificación aquí: Todos los campos son opcionales y tienen valor por defecto de None
class UpdateProfileRequest(BaseModel):
    email: Optional[str] = None
    username: Optional[str] = None
    password: Optional[str] = None
    birthdate: Optional[str] = None
    gender: Optional[str] = None
@app.post("/register")
def register(request: RegisterRequest, db: Session = Depends(get_db)):
    return register_user(db, request)


@app.post("/logout")
def logout(token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)):
    return logout_user(db, token)


@app.get("/profile")
def get_profile(user_id: int = Depends(get_current_user), db: Session = Depends(get_db)):
    return get_user_profile(db, user_id)

@app.post("/profile/update")
def update_profile(request: UpdateProfileRequest, user_id: int = Depends(get_current_user), db: Session = Depends(get_db)):
    return update_user_profile(db, user_id, request)

@app.post("/import-data")
def import_data(data_type: str, file: UploadFile = File(...), user: int = Depends(get_current_user), db: Session = Depends(get_db)):
    return import_sensor_data(db, user, data_type, file)

@app.get("/dashboard/view")
def dashboard_view(user_id: int = Depends(get_current_user), db: Session = Depends(get_db)):
    return get_dashboard_view(db, user_id)


@app.get("/dashboard/history")
def data_history(data_type: str, period: str, user: dict = Depends(get_current_user), db: Session = Depends(get_db)):
    return get_data_history(db, user, data_type, period)

@app.post("/add-dummy-user")
def add_dummy_user_route(db: Session = Depends(get_db)):
    return add_dummy_user(db)
