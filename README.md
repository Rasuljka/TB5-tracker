# "Трекер задач сотрудников"

## Для запуска приложения необходимо выполнить следующие команды:

```pip install -r requirements.txt```

```uvicorn app.main:app --reload```

Эта команда запустит сервер uvicorn и загрузит ваше приложение на FastAPI. 
Параметр «—reload» указывает серверу на автоматическую перезагрузку приложения при изменении кода.

## Чтобы посмотреть документацию по проекту введите:

```http://127.0.0.1:8000/docs#/```
