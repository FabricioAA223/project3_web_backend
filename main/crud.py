from sqlalchemy.orm import Session
from .models import User
from datetime import datetime
from fastapi import HTTPException

# Función para iniciar sesión
def login_user(db: Session, username: str, password: str):
    user = db.query(User).filter(User.username == username).first()
    if user and user.verify_password(password):
        # Lógica para crear un token de sesión
        return {"status": "success", "message": "Login successful"}
    raise HTTPException(status_code=400, detail="Incorrect username or password")

# Función para registrar un usuario
def register_user(db: Session, request):
    new_user = User(
        email=request.email,
        username=request.username,
        password=User.hash_password(request.password),
        weight=request.weight,
        height=request.height,
        birthdate=request.birthdate,
        gender=request.gender,
        created_at=datetime.utcnow()
    )
    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    return {"status": "success", "message": "User registered successfully"}

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
