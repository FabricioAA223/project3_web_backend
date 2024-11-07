from sqlite3 import IntegrityError
import jwt  # Importa PyJWT para trabajar con tokens
from datetime import datetime, timedelta
from sqlalchemy.orm import Session
from .models import User, Weight, Height, BodyComposition, BodyFatPercentage, WaterConsumption, DailySteps, Exercise
from fastapi import HTTPException, UploadFile
from .schemas import GeneroEnum
from passlib.context import CryptContext
import pandas as pd
from sqlalchemy import func


pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


# Clave secreta para generar tokens 
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
    
    if user is None:
        return None  # Usuario no encontrado
    
    # Verificar si la contraseña es la misma (comparación en texto plano)
    if user.password == password:
        return user  # Contraseña correcta, se devuelve el usuario
    else:
        return None  # Contraseña incorrecta

    
    

    
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
def import_sensor_data(db: Session, user_id: int, data_type: str, file: UploadFile):
    try:
        # Leer el archivo CSV y eliminar espacios iniciales
        df = pd.read_csv(file.file, delimiter=',', skipinitialspace=True)
        
        # Eliminar espacios en los nombres de las columnas
        df.columns = df.columns.str.strip().astype(str).str.replace(';+', '', regex=True)
        
        # Identificar la última columna
        last_column = df.columns[-1]
        
        # Limpiar los valores en la última columna para eliminar `;;;` y convertir a numérico si es posible
        df[last_column] = df[last_column].astype(str).str.replace(';+', '', regex=True)
        print(df.head())

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
    # Calcula la fecha inicial según el período
    today = datetime.today()
    if period == 'week':
        start_date = today - timedelta(weeks=1)
    elif period == 'month':
        start_date = today - timedelta(days=30)
    elif period == 'three_months':
        start_date = today - timedelta(days=90)
    elif period == 'six_months':
        start_date = today - timedelta(days=180)
    elif period == 'year':
        start_date = today - timedelta(days=365)
    else:
        return {"status": "error", "message": "Invalid period"}

    # Mapea el data_type a la tabla correspondiente
    data_type_map = {
        'weights': {"table":Weight, "column":"weight", "label":"Peso (kg)"},
        'muscle': {"table":BodyComposition, "column":"muscle", "label":"Músculo"}, #Pero a la columna Muscle
        'body_fat_percentage': {"table":BodyFatPercentage, "column":"fatPercentage", "label":"Porcentaje de grasa corporal (%)"},
        'water_consumption': {"table":WaterConsumption, "column":"waterAmount", "label":"Vasos de agua"},
        'steps': {"table":DailySteps, "column":"stepsAmount", "label":"Pasos durante el día"},
        # 'exercises': {"table":Exercise, "column":"waterAmount", "label":"Vasos de agua"}, 
        # Tengo que ver que hago con los ejercicios
    }
    if data_type == 'exercises':
        results = db.query(Exercise.date, Exercise.exerciseName, Exercise.duration) \
                    .filter(Exercise.userId == user_id)\
                    .filter(Exercise.date >= start_date)\
                    .order_by(Exercise.date.asc())\
                    .all()

        # Manejo de resultados vacíos
        if not results:
            return {"status": "success", "data": []}
        
        data = [{"fecha": record.date, record.exerciseName: record.duration} for record in results]

        return {"status": "success", "data": data}
    
    elif data_type not in data_type_map:
        return {"status": "error", "message": "Invalid data_type"}
    
    # Selecciona la tabla correspondiente
    table_info = data_type_map[data_type]
    table = table_info["table"]
    column_name = table_info["column"]

    # Consulta SQL: Filtra por user_id y fecha en el rango, y selecciona los valores y fechas
    results = db.query(table.date, getattr(table, column_name)) \
                .filter(table.userId == user_id)\
                .filter(table.date >= start_date)\
                .order_by(table.date.asc())\
                .all()

    # Manejo de resultados vacíos
    if not results:
        return {"status": "success", "data": []}
    
    # Prepara los datos para el gráfico
    data = [{"fecha": record.date, table_info["label"]: record[1]} for record in results]

    return {"status": "success", "data": data}