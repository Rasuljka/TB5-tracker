import os

from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

# Настройка подключения к базе данных
username = os.getenv('USERNAME')
password = os.getenv('PASSWORD')
dbname = os.getenv('DBNAME')

DATABASE_URL = f"postgresql://{username}:{password}@localhost/{dbname}"  # Замените username, password и dbname на ваши данные

# Создание движка для подключения к базе данных
engine = create_engine(DATABASE_URL)

# Создание базового класса для всех моделей данных
Base = declarative_base()

# Создание фабрики сессий для взаимодействия с базой данных
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
