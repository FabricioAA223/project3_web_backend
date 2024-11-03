import asyncio
from sqlalchemy.future import select
from database import SessionLocal
from models import User

async def check_password_hashes():
    async with SessionLocal() as db:
        result = await db.execute(select(User))
        users = result.scalars().all()

        for user in users:
            if not user.password.startswith("$2b$") and not user.password.startswith("$2a$"):
                print(f"El usuario '{user.username}' tiene una contraseña que no está hasheada correctamente.")
            else:
                print(f"El usuario '{user.username}' tiene una contraseña hasheada correctamente.")

# Ejecuta la función asíncrona
asyncio.run(check_password_hashes())
