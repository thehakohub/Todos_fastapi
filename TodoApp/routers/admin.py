from loggers import get_logger
import sys
from typing import Annotated, TypeAlias
from sqlalchemy.orm import Session
from fastapi import APIRouter, Depends, HTTPException, Path
from starlette import status
from database_models import Todos
from routers import auth
from database import SessionLocal
from models import TodoRequest
from .auth import get_current_user


router = APIRouter(
    prefix="/admin",
    tags=["admin"]
)

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

db_dependency : TypeAlias = Annotated[Session, Depends(get_db)]

user_dependency : TypeAlias = Annotated[dict, Depends(get_current_user)]
logger = get_logger(__name__)

@router.get("/todo", status_code=status.HTTP_200_OK)
async def get_todos(db: db_dependency, current_user: user_dependency):
    logger.info(f"Current user: {current_user}")
    if  current_user is None or current_user.get("user_role") !=  'admin':
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to access this resource"
        )
    todos = db.query(Todos).all()
    return todos

@router.delete("/todo/{todo_id}", status_code=status.HTTP_200_OK)
async def delete_todo(user:user_dependency, db: db_dependency, 
                      todo_id: int = Path(gt=0, description="ID of the todo to delete")):
    logger.info(f"Current user: {user}")
    if  user is None or user.get("user_role") !=  'admin':
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to access this resource"
        )
    todo = db.query(Todos).filter(Todos.id == todo_id).first()
    if not todo:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Todo not found"
        )
    db.delete(todo)
    db.commit()
    return {"detail": "Todo deleted successfully"}