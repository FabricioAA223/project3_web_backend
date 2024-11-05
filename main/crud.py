from sqlite3 import IntegrityError
import jwt  # Importa PyJWT para trabajar con tokens
from datetime import datetime, timedelta
from sqlalchemy.orm import Session
from .models import User, Weight, Height
from fastapi import HTTPException
from .schemas import GeneroEnum
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
    # Buscar el usuario en la base de datos por nombre de usuario
    user = db.query(User).filter(User.username == username).first()
    
    # Verificar si el usuario fue encontrado
    if not user:
        raise HTTPException(status_code=400, detail="Usuario no encontrado")
    
    # Comparar la contraseña (aquí es donde deberías usar hashing en producción)
    if user.password != password:
        raise HTTPException(status_code=400, detail="Contraseña incorrecta")
    
    # Retornar el objeto usuario si la autenticación fue exitosa
    return user

def register_user(db: Session, email: str, username: str, password: str, birthday: str, gender: GeneroEnum, weight: float, height: float): 
    # Verificar si el usuario ya existe
    existing_user = db.query(User).filter(User.email == email).first()
    if existing_user:
        raise HTTPException(status_code=400, detail="El correo electrónico ya está registrado")

    # Crear un nuevo usuario
    new_user = User(email=email, username=username, password=password, birthday=birthday, gender=gender)
    
    # Agregar el nuevo usuario a la sesión
    db.add(new_user)
    db.commit()
    db.refresh(new_user)  # Obtener el usuario recién creado con el ID generado

    # Crear registros de peso y altura
    weight_record = Weight(user_id=new_user.id, weight=weight)  # Peso actual
    height_record = Height(user_id=new_user.id, height=height)  # Altura actual
    
    # Agregar los registros a la sesión
    db.add(weight_record)
    db.add(height_record)

    # Confirmar los cambios en la base de datos
    db.commit()

    return {"message": "Usuario registrado exitosamente", "user_id": new_user.id}

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
