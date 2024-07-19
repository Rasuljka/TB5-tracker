from pydantic import BaseModel
from typing import Optional


class TaskIn(BaseModel):
    title: str
    parent_task_id: Optional[int] = None
    assignee_id: int
    deadline: str
    status: str


class TaskOut(BaseModel):
    id: int
    title: str
    parent_task_id: Optional[int] = None
    assignee_id: int
    deadline: str
    status: str


class EmployeeIn(BaseModel):
    name: str
    job_title: str


class EmployeeOut(BaseModel):
    id: int
    name: str
    job_title: str
