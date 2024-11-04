from datetime import datetime
from fastapi import HTTPException, UploadFile
import pandas as pd
from sqlalchemy import func
from sqlalchemy.orm import Session
from .models import User, Weight, Height, BodyComposition, BodyFatPercentage, WaterConsumption, DailySteps, Exercise

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
# def import_sensor_data(db: Session, data_type: str, file):
#     # Lógica para procesar el archivo CSV y almacenar los datos
#     return {"status": "success", "message": "Data imported successfully"}
def import_sensor_data(db: Session, user_id: int, data_type: str, file: UploadFile):
    try:
        df = pd.read_csv(file.file)
        if data_type == 'weights':
            for _, row in df.iterrows():
                new_weight = Weight(
                    date=row['fecha'],
                    userId=user_id,
                    weight=row['peso']
                )
                db.merge(new_weight)
        elif data_type == 'heights':
            for _, row in df.iterrows():
                new_height = Height(
                    date=row['fecha'],
                    userId=user_id,
                    height=row['altura']
                )
                db.merge(new_height)
        elif data_type == 'body_composition':
            for _, row in df.iterrows():
                new_body_composition = BodyComposition(
                    date=row['fecha'],
                    userId=user_id,
                    fat=row['grasa'],
                    muscle=row['musculo'],
                    water=row['agua']
                )
                db.merge(new_body_composition)
        elif data_type == 'body_fat_percentage':
            for _, row in df.iterrows():
                new_body_fat = BodyFatPercentage(
                    date=row['fecha'],
                    userId=user_id,
                    fatPercentage=row['porcentajeGrasa']
                )
                db.merge(new_body_fat)
        elif data_type == 'water_consumption':
            for _, row in df.iterrows():
                new_water_consumption = WaterConsumption(
                    date=row['fecha'],
                    userId=user_id,
                    waterAmount=row['vasosDeAgua']
                )
                db.merge(new_water_consumption)
        elif data_type == 'daily_steps':
            for _, row in df.iterrows():
                new_daily_steps = DailySteps(
                    date=row['fecha'],
                    userId=user_id,
                    stepsAmount=row['cantidadPasos']
                )
                db.merge(new_daily_steps)
        elif data_type == 'exercises':
            for _, row in df.iterrows():
                new_exercise = Exercise(
                    date=row['fecha'],
                    userId=user_id,
                    exerciseName=row['nombreEjercicio'],
                    duration=row['duracion']
                )
                db.merge(new_exercise)
        else:
            raise HTTPException(status_code=400, detail="Tipo de datos no válido para importación")

        db.commit()
        return {"status": "success", "message": "Data imported successfully"}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


# Función para cargar la vista general del dashboard
# def get_dashboard_view(db: Session, user_id: int):
#     # Consultas SQL con MAX basado en fecha para cada elemento esperado
#     return {"status": "success", "data": "Dashboard data"}
# Implementación mejorada de la función get_dashboard_view
# Implementación mejorada de la función get_dashboard_view

def get_dashboard_view(db: Session, user_id: int):
    try:
        # Peso Actual
        weight = db.query(Weight).filter(Weight.userId == user_id).order_by(Weight.date.desc()).first()
        # Altura Actual
        height = db.query(Height).filter(Height.userId == user_id).order_by(Height.date.desc()).first()
        # Composición Corporal Actual
        body_composition = db.query(BodyComposition).filter(BodyComposition.userId == user_id).order_by(BodyComposition.date.desc()).first()
        # Porcentaje de Grasa Corporal
        body_fat = db.query(BodyFatPercentage).filter(BodyFatPercentage.userId == user_id).order_by(BodyFatPercentage.date.desc()).first()
        # Consumo de Agua Hoy
        water_consumption = db.query(func.sum(WaterConsumption.waterAmount)).filter(
            WaterConsumption.userId == user_id,
            func.date(WaterConsumption.date) == func.current_date()
        ).scalar()
        # Pasos Dados Hoy
        daily_steps = db.query(func.sum(DailySteps.stepsAmount)).filter(
            DailySteps.userId == user_id,
            func.date(DailySteps.date) == func.current_date()
        ).scalar()
        # Ejercicios Realizados Hoy
        exercises = db.query(Exercise).filter(
            Exercise.userId == user_id,
            func.date(Exercise.date) == func.current_date()
        ).all()

        return {
            "status": "success",
            "data": {
                "weight": weight.weight if weight else None,
                "height": height.height if height else None,
                "body_composition": {
                    "fat": body_composition.fat if body_composition else None,
                    "muscle": body_composition.muscle if body_composition else None,
                    "water": body_composition.water if body_composition else None,
                },
                "body_fat_percentage": body_fat.fatPercentage if body_fat else None,
                "water_consumption_today": water_consumption if water_consumption else 0,
                "daily_steps": daily_steps if daily_steps else 0,
                "exercises_today": [{"name": e.exerciseName, "duration": e.duration} for e in exercises]
            }
        }
    except Exception as e:
        return {
            "status": "error",
            "message": str(e)
        }
    
def add_dummy_user(db: Session):
    try:
        dummy_user = User(
            email="dummyuser@example.com",
            username="dummyuser",
            password="olman123", 
            birthday="2000-01-01",
            gender="MASCULINO"
        )
        db.merge(dummy_user)
        db.commit()
        return {"status": "success", "message": "Dummy user added successfully"}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


# Función para cargar el histórico de datos
def get_data_history(db: Session, user_id: int, data_type: str, period: str):
    # Consultas SQL basadas en el periodo de tiempo seleccionado
    return {"status": "success", "data": "Historical data"}
