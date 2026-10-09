from datetime import date

from sqlalchemy import case, func, select
from sqlalchemy.orm import Session

from app.models.task import Task
from app.schemas.task import Priority, TaskCreate, TaskStatus, TaskUpdate


def create_task(db: Session, data: TaskCreate) -> Task:
    task = Task(**data.model_dump())
    db.add(task)
    db.commit()
    db.refresh(task)
    return task

def get_task(db: Session, task_id: int) -> Task | None:
    return db.get(Task, task_id)

def list_tasks(db: Session, status: TaskStatus | None = None, priority: Priority | None = None,
               search: str | None = None, due_before: date | None = None,
               sort_by: str = "created_at", sort_order: str = "desc", limit: int = 20,
               offset: int = 0) -> list[Task]:
    query = select(Task)
    if status is not None:
        query = query.where(Task.status == status)
    if priority is not None:
        query = query.where(Task.priority == priority)
    if search:
        escaped = search.replace(chr(92), chr(92)*2).replace("%", chr(92)+"%").replace("_", chr(92)+"_")
        query = query.where(Task.title.ilike(f"%{escaped}%", escape=chr(92)))
    if due_before is not None:
        query = query.where(Task.due_date <= due_before)
    columns = {"created_at": Task.created_at, "due_date": Task.due_date,
               "priority": case((Task.priority == Priority.low, 1),
                                (Task.priority == Priority.medium, 2),
                                (Task.priority == Priority.high, 3), else_=0)}
    col = columns[sort_by]
    order = col.desc() if sort_order == "desc" else col.asc()
    query = query.order_by(order, Task.id.desc() if sort_order == "desc" else Task.id.asc())
    return list(db.scalars(query.limit(limit).offset(offset)).all())

def update_task(db: Session, task: Task, data: TaskUpdate) -> Task:
    for field, value in data.model_dump(exclude_unset=True).items():
        setattr(task, field, value)
    db.commit()
    db.refresh(task)
    return task

def delete_task(db: Session, task: Task) -> None:
    db.delete(task)
    db.commit()

def get_task_stats(db: Session) -> dict:
    result = {"total": db.scalar(select(func.count()).select_from(Task)) or 0,
              "todo": 0, "in_progress": 0, "done": 0}
    for status, count in db.execute(select(Task.status, func.count()).group_by(Task.status)):
        result[status.value] = count
    return result
