from datetime import date
from typing import Annotated, Literal

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session

from app.db.database import get_db
from app.schemas.task import Priority, TaskCreate, TaskResponse, TaskStatus, TaskUpdate
from app.services import task_service

router = APIRouter(prefix="/tasks", tags=["Tasks"])
DbSession = Annotated[Session, Depends(get_db)]

@router.post("/", response_model=TaskResponse, status_code=201)
def create_task(data: TaskCreate, db: DbSession):
    return task_service.create_task(db, data)

@router.get("/", response_model=list[TaskResponse])
def list_tasks(db: DbSession, status: TaskStatus | None = None, priority: Priority | None = None,
               search: str | None = Query(default=None, max_length=200), due_before: date | None = None,
               sort_by: Literal["created_at", "due_date", "priority"] = "created_at",
               sort_order: Literal["asc", "desc"] = "desc",
               limit: int = Query(default=20, ge=1, le=100), offset: int = Query(default=0, ge=0)):
    return task_service.list_tasks(db, status, priority, search, due_before, sort_by, sort_order, limit, offset)

@router.get("/{task_id}", response_model=TaskResponse)
def get_task(task_id: int, db: DbSession):
    task = task_service.get_task(db, task_id)
    if task is None:
        raise HTTPException(404, "Task not found")
    return task

@router.patch("/{task_id}", response_model=TaskResponse)
def update_task(task_id: int, data: TaskUpdate, db: DbSession):
    task = task_service.get_task(db, task_id)
    if task is None:
        raise HTTPException(404, "Task not found")
    return task_service.update_task(db, task, data)

@router.delete("/{task_id}", status_code=204)
def delete_task(task_id: int, db: DbSession):
    task = task_service.get_task(db, task_id)
    if task is None:
        raise HTTPException(404, "Task not found")
    task_service.delete_task(db, task)
