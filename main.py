from sqlalchemy import create_engine
from config.settings import Base, DATABASE_URL

# Создание движка для подключения к базе данных
engine = create_engine(DATABASE_URL)

# Создание всех таблиц в базе данных
Base.metadata.create_all(bind=engine)
