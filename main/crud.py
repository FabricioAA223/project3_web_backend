from sqlite3 import IntegrityError
import jwt  # Importa PyJWT para trabajar con tokens
from datetime import datetime, timedelta
from sqlalchemy.orm import Session
from .models import User
from fastapi import HTTPException
from .schemas import RegisterRequest
from passlib.context import CryptContext

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def hash_password(password: str) -> str:
    return pwd_context.hash(password)


# Clave secreta para generar tokens (esta debe ser segura y mantenerse privada)
SECRET_KEY = "YOUR_SECRET_KEY"
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30

# Función para crear un token JWT
def create_access_token(data: dict):
    to_encode = data.copy()
    expire = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode.update({"exp": expire})
    return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)

# Función para iniciar sesión
def login_user(db: Session, username: str, password: str):
    user = db.query(User).filter(User.username == username).first()
    
    # Verifica si el usuario existe y la contraseña es correcta
    if user and user.verify_password(password):
        # Genera un token de sesión (implementa create_access_token si no lo tienes)
        access_token = create_access_token(data={"sub": user.username})
        return {"access_token": access_token, "token_type": "bearer"}
    
    raise HTTPException(status_code=400, detail="Incorrect username or password")

def register_user(db: Session, email: str, username: str, password: str, birthday: str, gender: str):
    # Verifica si el usuario ya existe
    existing_user = db.query(User).filter((User.email == email) | (User.username == username)).first()
    if existing_user:
        raise HTTPException(status_code=400, detail="Email or username already registered")

    # Crea un nuevo usuario
    new_user = User(
        email=email,
        username=username,
        password=hash_password(password),
        birthday=birthday,
        gender=gender
    )
    
    # Añade el nuevo usuario a la sesión de la base de datos
    db.add(new_user)
    
    # Realiza el commit para guardar los cambios
    db.commit()
    
    # Refresca la instancia para obtener el ID del usuario
    db.refresh(new_user)

    return new_user 

# Función para cerrar sesión
def logout_user(db: Session, token: str):
    # Lógica para invalidar el token
    return {"status": "success", "message": "Logout successful"}

# Función para obtener el perfil del usuario
def get_user_profile(db: Session, user_id: int):
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return user

# Función para actualizar el perfil del usuario
def update_user_profile(db: Session, user_id: int, request):
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    for key, value in request.dict().items():
        if value is not None:
            setattr(user, key, value)
    db.commit()
    return {"status": "success", "message": "Profile updated successfully"}

# Función para importar datos de sensores
def import_sensor_data(db: Session, data_type: str, file):
    # Lógica para procesar el archivo CSV y almacenar los datos
    return {"status": "success", "message": "Data imported successfully"}

# Función para cargar la vista general del dashboard
def get_dashboard_view(db: Session, user_id: int):
    # Consultas SQL con MAX basado en fecha para cada elemento esperado
    return {"status": "success", "data": "Dashboard data"}

# Función para cargar el histórico de datos
def get_data_history(db: Session, user_id: int, data_type: str, period: str):
    # Consultas SQL basadas en el periodo de tiempo seleccionado
    return {"status": "success", "data": "Historical data"}
