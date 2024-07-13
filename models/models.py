from sqlalchemy import Column, Integer, String, ForeignKey
from sqlalchemy.orm import relationship

from config.settings import Base


class Employee(Base):
    __tablename__: str = 'Employees'
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, index=True)
    tasks = relationship("Task", back_populates="employee")


class Task(Base):
    __tablename__ = 'Tasks'
    id = Column(Integer, primary_key=True, index=True)
    title = Column(String, index=True)
    description = Column(String)
    employee_id = Column(Integer, ForeignKey('Employees.id'))
    employee = relationship("Employee", back_populates="tasks")
    project_id = Column(Integer, ForeignKey('Projects.id'))
    project = relationship("Project", back_populates="tasks")
    status_id = Column(Integer, ForeignKey('Statuses.id'))
    status = relationship("Status", back_populates="tasks")
