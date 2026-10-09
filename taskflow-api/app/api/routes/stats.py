from typing import Annotated
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.db.database import get_db
from app.schemas.task import TaskStats
from app.services import task_service

router = APIRouter(prefix="/stats", tags=["Statistics"])

@router.get("/", response_model=TaskStats)
def get_stats(db: Annotated[Session, Depends(get_db)]):
    return task_service.get_task_stats(db)
