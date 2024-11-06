import enum
from sqlalchemy.orm import relationship
from datetime import datetime, timezone
from .database import Base
from passlib.context import CryptContext
from sqlalchemy import Column, Integer, String, Enum as SQLAlchemyEnum, Float, ForeignKey, DateTime, Date

# Inicializa el contexto de encriptación
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

class GeneroEnum(enum.Enum):
    MASCULINO = "MASCULINO"
    FEMENINO = "FEMENINO"

class User(Base):
    __tablename__ = "users"
    
    id = Column(Integer, primary_key=True, index=True)
    email = Column(String, unique=True, nullable=False)  # Correo único
    username = Column(String, unique=True, nullable=False)  # Asegurarse de que sea único
    password = Column(String, nullable=False)
    birthday = Column(Date, nullable=False)  # Cambio a Date
    gender = Column(SQLAlchemyEnum(GeneroEnum, name="generoenum"), nullable=False)
    
    # Relaciones con otras tablas
    weights = relationship("Weight", back_populates="user", cascade="all, delete-orphan")
    heights = relationship("Height", back_populates="user", cascade="all, delete-orphan")
    water_consumption = relationship("WaterConsumption", back_populates="user", cascade="all, delete-orphan")
    body_fat_percentage = relationship("BodyFatPercentage", back_populates="user", cascade="all, delete-orphan")
    daily_steps = relationship("DailySteps", back_populates="user", cascade="all, delete-orphan")
    exercises = relationship("Exercise", back_populates="user", cascade="all, delete-orphan")
    body_composition = relationship("BodyComposition", back_populates="user", cascade="all, delete-orphan")
    
class Weight(Base):
    __tablename__ = "weights"
    
    date = Column(DateTime, primary_key=True, index=True, default=lambda: datetime.now(timezone.utc))
    user_id = Column("userId",Integer, ForeignKey('users.id'), primary_key=True, index=True, nullable=False)
    weight = Column(Float, nullable=False)
    
    user = relationship("User", back_populates="weights")

class Height(Base):
    __tablename__ = "heights"
    
    date = Column(DateTime, primary_key=True, index=True, default=lambda: datetime.now(timezone.utc))
    user_id = Column("userId", Integer, ForeignKey('users.id'), primary_key=True, index=True, nullable=False)
    height = Column(Float, nullable=False)
    
    user = relationship("User", back_populates="heights")

class WaterConsumption(Base):
    __tablename__ = "water_consumption"
    
    date = Column(DateTime, primary_key=True, index=True, default=lambda: datetime.now(timezone.utc))
    user_id = Column(Integer, ForeignKey('users.id'), primary_key=True, index=True, nullable=False)
    water_amount = Column(Integer, nullable=False)
    
    user = relationship("User", back_populates="water_consumption")

class BodyFatPercentage(Base):
    __tablename__ = "body_fat_percentage"
    
    date = Column(DateTime, primary_key=True, index=True, default=lambda: datetime.now(timezone.utc))
    user_id = Column(Integer, ForeignKey('users.id'), primary_key=True, index=True, nullable=False)
    fat_percentage = Column(Float, nullable=False)
    
    user = relationship("User", back_populates="body_fat_percentage")

class DailySteps(Base):
    __tablename__ = "daily_steps"
    
    date = Column(DateTime, primary_key=True, index=True, default=lambda: datetime.now(timezone.utc))
    user_id = Column(Integer, ForeignKey('users.id'), primary_key=True, index=True, nullable=False)
    steps_amount = Column(Integer, nullable=False)
    
    user = relationship("User", back_populates="daily_steps")

class Exercise(Base):
    __tablename__ = "exercises"
    
    date = Column(DateTime, primary_key=True, index=True, default=lambda: datetime.now(timezone.utc))
    user_id = Column(Integer, ForeignKey('users.id'), primary_key=True, index=True, nullable=False)
    exercise_name = Column(String, nullable=False)
    duration = Column(Integer, nullable=False)
    
    user = relationship("User", back_populates="exercises")

class BodyComposition(Base):
    __tablename__ = "body_composition"
    
    date = Column(DateTime, primary_key=True, index=True, default=lambda: datetime.now(timezone.utc))
    user_id = Column(Integer, ForeignKey('users.id'), primary_key=True, index=True, nullable=False)
    fat = Column(Float, nullable=False)
    muscle = Column(Float, nullable=False)
    water = Column(Float, nullable=False)
    
    user = relationship("User", back_populates="body_composition")
