from sqlalchemy import Column, Integer, String, ForeignKey
from sqlalchemy.orm import relationship

from database import Base, engine


class Task(Base):
    __tablename__ = "tasks"
    id = Column(Integer, primary_key=True, index=True)
    title = Column(String, index=True)
    parent_task_id = Column(Integer, ForeignKey("tasks.id"), nullable=True)
    assignee_id = Column(Integer, ForeignKey("employees.id"), nullable=True)
    deadline = Column(String, index=True)
    status = Column(String, index=True)
    parent_task = relationship("Task", remote_side=[id])
    assignee = relationship("Employee", back_populates="tasks")

    @property
    def is_important(self):
        return self.status == "not started" and any(
            child.status == "active" for child in self.children
        )


class Employee(Base):
    __tablename__ = "employees"
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, index=True)
    job_title = Column(String, index=True)
    tasks = relationship("Task", back_populates="employee")

    @property
    def active_tasks_count(self):
        return len([task for task in self.tasks if task.status == "active"])


Task.employee = relationship("Employee", back_populates="tasks")

Base.metadata.create_all(bind=engine)
