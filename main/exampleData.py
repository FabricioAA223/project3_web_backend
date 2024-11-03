from sqlalchemy.orm import Session
from .models import User, GeneroEnum  # Importa User y GeneroEnum
from datetime import datetime

def exampleData(db: Session):
    # Datos de ejemplo para usuarios
    users = [
        User(
            email="user1@example.com",
            username="user1",
            password="hashed_password1",  # Reemplaza con un hash real
            birthday="1990-01-01",
            gender=GeneroEnum.MASCULINO
        ),
        User(
            email="marsol@gmail.com",
            username="Majo",
            password="123Mjsg",  # Reemplaza con un hash real
            birthday="2003-03-03",
            gender=GeneroEnum.FEMENINO
        ),
    ]

    # Agregar los usuarios a la sesión de base de datos
    for user in users:
        db.add(user)

    # Confirmar los cambios en la base de datos
    db.commit()
    print("Datos de ejemplo agregados a la base de datos.")

    #imprimir los datos de los usuarios
    for user in db.query(User).all():
        print(user.email, user.username, user.birthday, user.password)
