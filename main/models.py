import enum
from sqlalchemy import Column, Enum, Float, ForeignKey, Integer, String, DateTime
from sqlalchemy.orm import relationship
from datetime import datetime, timezone
from .database import Base

class GeneroEnum(enum.Enum):
    MASCULINO = "Masculino"
    FEMENINO = "Femenino"

class User(Base):
    __tablename__ = "users"
    id = Column(Integer, primary_key=True, index=True)
    email = Column(String, nullable=False)
    username = Column(String, nullable=False)
    password = Column(String, nullable=False)
    birthday = Column(String, nullable=False)
    gender = Column(Enum(GeneroEnum), nullable=False)  # Solo permite "Masculino" o "Femenino"

class Weight(Base):
    __tablename__ = "weights"
    date = Column(DateTime, primary_key=True, index=True)
    userId = Column(Integer, ForeignKey('users.id'), primary_key=True, index=True, nullable=False)

    weight = Column(Float, nullable=False)

class Height(Base):
    __tablename__ = "heights"
    date = Column(DateTime, primary_key=True, index=True)
    userId = Column(Integer, ForeignKey('users.id'), primary_key=True, index=True, nullable=False)

    height = Column(Float, nullable=False)

class WaterConsumption(Base):
    __tablename__ = "waterConsumption"
    date = Column(DateTime, primary_key=True, index=True)
    userId = Column(Integer, ForeignKey('users.id'), primary_key=True, index=True, nullable=False)

    waterAmount = Column(Integer, nullable=False)

class BodyFatPercentage(Base):
    __tablename__ = "bodyFatPercentage"
    date = Column(DateTime, primary_key=True, index=True)
    userId = Column(Integer, ForeignKey('users.id'), primary_key=True, index=True, nullable=False)

    fatPercentage = Column(Float, nullable=False)

class DailySteps(Base):
    __tablename__ = "dailySteps"
    date = Column(DateTime, primary_key=True, index=True)
    userId = Column(Integer, ForeignKey('users.id'), primary_key=True, index=True, nullable=False)

    stepsAmount = Column(Integer, nullable=False)

class Exercise(Base):
    __tablename__ = "exercises"
    date = Column(DateTime, primary_key=True, index=True)
    userId = Column(Integer, ForeignKey('users.id'), primary_key=True, index=True, nullable=False)

    exerciseName = Column(String, nullable=False)
    duration = Column(Integer, nullable=False)

class BodyComposition(Base):
    __tablename__ = "bodyComposition"
    date = Column(DateTime, primary_key=True, index=True)
    userId = Column(Integer, ForeignKey('users.id'), primary_key=True, index=True, nullable=False)

    fat = Column(Float, nullable=False)
    muscle = Column(Float, nullable=False)
    water = Column(Float, nullable=False)