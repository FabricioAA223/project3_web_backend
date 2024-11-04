from pydantic import BaseModel, Field, EmailStr
from typing import Literal
from datetime import date, datetime
from enum import Enum

# Esquema para el Genero
class GeneroEnum(str, Enum):
    MASCULINO = "MASCULINO"
    FEMENINO = "FEMENINO"

class RegisterRequest(BaseModel):
    email: EmailStr  # Asegúrate de que sea un correo electrónico válido
    username: str
    password: str
    birthday: date  # Cambio a Date
    gender: GeneroEnum

    class Config:
        orm_mode = True  # Permite que se use el modelo ORM

# Esquema para el Usuario
class UserBase(BaseModel):
    email: EmailStr
    username: str
    birthday: str
    gender: GeneroEnum

class UserCreate(UserBase):
    password: str  # Solo requerido en la creación

class User(UserBase):
    id: int

    class Config:
        orm_mode = True

# Esquema para el Peso (Weight)
class WeightBase(BaseModel):
    date: datetime
    weight: float = Field(..., gt=0)  # Peso positivo

class WeightCreate(WeightBase):
    userId: int

class Weight(WeightBase):
    userId: int

    class Config:
        orm_mode = True

# Esquema para la Altura (Height)
class HeightBase(BaseModel):
    date: datetime
    height: float = Field(..., gt=0)  # Altura positiva

class HeightCreate(HeightBase):
    userId: int

class Height(HeightBase):
    userId: int

    class Config:
        orm_mode = True

# Esquema para el Consumo de Agua (WaterConsumption)
class WaterConsumptionBase(BaseModel):
    date: datetime
    waterAmount: int = Field(..., gt=0)  # Cantidad positiva de agua

class WaterConsumptionCreate(WaterConsumptionBase):
    userId: int

class WaterConsumption(WaterConsumptionBase):
    userId: int

    class Config:
        orm_mode = True

# Esquema para el Porcentaje de Grasa Corporal (BodyFatPercentage)
class BodyFatPercentageBase(BaseModel):
    date: datetime
    fatPercentage: float = Field(..., ge=0, le=100)  # Porcentaje de grasa entre 0 y 100

class BodyFatPercentageCreate(BodyFatPercentageBase):
    userId: int

class BodyFatPercentage(BodyFatPercentageBase):
    userId: int

    class Config:
        orm_mode = True

# Esquema para los Pasos Diarios (DailySteps)
class DailyStepsBase(BaseModel):
    date: datetime
    stepsAmount: int = Field(..., ge=0)  # Cantidad no negativa de pasos

class DailyStepsCreate(DailyStepsBase):
    userId: int

class DailySteps(DailyStepsBase):
    userId: int

    class Config:
        orm_mode = True

# Esquema para los Ejercicios (Exercise)
class ExerciseBase(BaseModel):
    date: datetime
    exerciseName: str
    duration: int = Field(..., gt=0)  # Duración positiva en minutos

class ExerciseCreate(ExerciseBase):
    userId: int

class Exercise(ExerciseBase):
    userId: int

    class Config:
        orm_mode = True

# Esquema para la Composición Corporal (BodyComposition)
class BodyCompositionBase(BaseModel):
    date: datetime
    fat: float = Field(..., ge=0, le=100)
    muscle: float = Field(..., ge=0, le=100)
    water: float = Field(..., ge=0, le=100)

class BodyCompositionCreate(BodyCompositionBase):
    userId: int

class BodyComposition(BodyCompositionBase):
    userId: int

    class Config:
        orm_mode = True
