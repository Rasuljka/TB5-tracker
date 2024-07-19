from fastapi import FastAPI, HTTPException
from typing import Dict
from sqlalchemy import func, select, exists
from sqlalchemy.dialects.postgresql import Any
from typing import List

from database import database
from models import Task, Employee
from schemas import TaskOut, TaskIn, EmployeeOut, EmployeeIn


app = FastAPI()


@app.on_event("startup")
async def startup():
    """Запуск"""
    await database.connect()


@app.on_event("shutdown")
async def shutdown():
    """Остановка"""
    await database.disconnect()


@app.post("/tasks/", response_model=TaskOut)
async def create_task(task: TaskIn):
    """Создание задачи"""
    async with database.transaction():
        query = Task.__table__.insert().values(
            title=task.title,
            parent_task_id=task.parent_task_id,
            assignee_id=task.assignee_id,
            deadline=task.deadline,
            status=task.status,
        )
        last_record_id = await database.execute(query)
        return {**task.dict(), "id": last_record_id}


@app.get("/tasks/", response_model=List[TaskOut])
async def read_tasks(skip: int = 0, limit: int = 10):
    """Чтение задачи"""
    query = Task.__table__.select().offset(skip).limit(limit)
    return await database.fetch_all(query)


@app.get("/tasks/{task_id}", response_model=TaskOut)
async def read_task(task_id: int):
    """Чтение задачи по ID"""
    query = Task.__table__.select().where(Task.__table__.c.id == task_id)
    task = await database.fetch_one(query)
    if task is None:
        raise HTTPException(status_code=404, detail="Task not found")
    return task


@app.put("/tasks/{task_id}", response_model=TaskOut)
async def update_task(task_id: int, task: TaskIn):
    """Обновление задачи"""
    query = (
        Task.__table__.update()
        .where(Task.__table__.c.id == task_id)
        .values(
            title=task.title,
            parent_task_id=task.parent_task_id,
            assignee_id=task.assignee_id,
            deadline=task.deadline,
            status=task.status,
        )
    )
    await database.execute(query)
    return {**task.dict(), "id": task_id}


@app.delete("/tasks/{task_id}")
async def delete_task(task_id: int):
    """Удаление задачи"""
    query = Task.__table__.delete().where(Task.__table__.c.id == task_id)
    await database.execute(query)
    return {"message": "Task deleted"}


@app.get("/important_tasks/", response_model=List[TaskOut])
async def get_important_tasks():
    """Получает важные задачи"""
    query = (
        select(Task)
        .where(Task.status == "not started")
        .where(
            exists().where((Task.id == Task.parent_task_id) &
                           (Task.status == "active"))
        )
    )
    result = await database.fetch_all(query)
    return result


@app.get("/important_tasks_with_assignees/",
         response_model=List[Dict[str, Any]])
async def get_important_tasks_with_assignees():
    """Получает важные задачи, не взятые в работу,
    и от которых зависят другие задачи, взятые в работу"""
    important_tasks = await get_important_tasks()
    available_employees = await get_available_employees()

    result = []
    for task in important_tasks:
        suitable_employees = [
            emp
            for emp in available_employees
            if emp["task_count"]
            <= min(emp["task_count"] for emp in available_employees) + 2
        ]
        result.append(
            {
                "important_task": task,
                "deadline": task.deadline,
                "employees": [emp["name"] for emp in suitable_employees],
            }
        )
    return result


@app.post("/employees/", response_model=EmployeeOut)
async def create_employee(employee: EmployeeIn):
    """Создание сотрудника"""
    async with database.transaction():
        query = Employee.__table__.insert().values(
            name=employee.name, job_title=employee.job_title
        )
        last_record_id = await database.execute(query)
        return {**employee.dict(), "id": last_record_id}


@app.get("/employees/", response_model=List[EmployeeOut])
async def read_employees(skip: int = 0, limit: int = 10):
    """Чтение сотрудника"""
    query = Employee.__table__.select().offset(skip).limit(limit)
    return await database.fetch_all(query)


@app.get("/employees/{employee_id}", response_model=EmployeeOut)
async def read_employee(employee_id: int):
    """Чтение сотрудника по ID"""
    query = Employee.__table__.select().where(Employee.__table__.c.id == employee_id)
    employee = await database.fetch_one(query)
    if employee is None:
        raise HTTPException(status_code=404, detail="Employee not found")
    return employee


@app.put("/employees/{employee_id}", response_model=EmployeeOut)
async def update_employee(employee_id: int, employee: EmployeeIn):
    """Обновление сотрудника"""
    query = (
        Employee.__table__.update()
        .where(Employee.__table__.c.id == employee_id)
        .values(name=employee.name, job_title=employee.job_title)
    )
    await database.execute(query)
    return {**employee.dict(), "id": employee_id}


@app.delete("/employees/{employee_id}")
async def delete_employee(employee_id: int):
    """Удаление сотрудника"""
    query = Employee.__table__.delete().where(Employee.__table__.c.id == employee_id)
    await database.execute(query)
    return {"message": "Employee deleted"}


@app.get("/busy_employees/", response_model=List[EmployeeOut])
async def get_busy_employees():
    """Получает список занятых сотрудников"""
    query = (
        select(Employee)
        .join(Task, Employee.id == Task.assignee_id)
        .filter(Task.status == "active")
        .group_by(Employee.id)
        .order_by(func.count(Task.id).desc())
    )
    result = await database.fetch_all(query)
    return result


@app.get("/available_employees/", response_model=List[EmployeeOut])
async def get_available_employees():
    """Получает список свободных сотрудников"""
    subquery = (
        select([Task.assignee_id, func.count(Task.id).label("task_count")])
        .group_by(Task.assignee_id)
        .subquery()
    )
    query = (
        select(Employee)
        .outerjoin(subquery, Employee.id == subquery.c.assignee_id)
        .order_by(subquery.c.task_count)
    )
    employees = await database.fetch_all(query)
    return employees
