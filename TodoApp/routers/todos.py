import logging
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
    prefix="/todos",
    tags=["todos"]
)

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

db_dependency : TypeAlias = Annotated[Session, Depends(get_db)]

user_dependency : TypeAlias = Annotated[dict, Depends(get_current_user)]

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)
logger.addHandler(logging.StreamHandler(sys.stdout))



@router.get("/get-todos", status_code=status.HTTP_200_OK)
async def read_all(user : user_dependency, db : db_dependency ):
    if user is None:
        raise HTTPException(status_code=401, detail="User authentication failed")
    return db.query(Todos).filter(Todos.owner_id == user.get("id")).all()

@router.get("/get-todos/{todo_id}", status_code=status.HTTP_200_OK)
async def read_todo(user : user_dependency, db : db_dependency, todo_id : int = Path(gt=0)):
    if user is None:
                raise HTTPException(status_code=401, detail="User authentication failed")
    
    todo_model = db.query(Todos).filter(Todos.id == todo_id)\
                  .filter(Todos.owner_id == user.get("id"))\
                  .first()
    if todo_model is not None:
        return todo_model
    else:
        raise HTTPException(status_code=404 , detail=str(f'Todo not found: + {todo_id}'))

@router.post('/create-todo', status_code=status.HTTP_201_CREATED)
async def create_todo(user:user_dependency, db: db_dependency, todo_request : TodoRequest):
    try:
        if user is None:
            raise HTTPException(status_code=401, detail="User authentication failed")
        
        todo_model = Todos(**todo_request.model_dump(), owner_id = user.get("id"))
        db.add(todo_model)
        logger.info('Creating todo: {}'.format(todo_model.__dict__))
        db.commit()
        return 'Todo created'
    except Exception as e:
        logger.error('Error creating todo: {}'.format(e))
        raise HTTPException(status_code=400 , detail=str(e))
    finally:
        db.close()
@router.put("/todo-update/{todo_id}", status_code=status.HTTP_204_NO_CONTENT)
async def update_todo(user: user_dependency, todo_request : TodoRequest, db : db_dependency, todo_id:int = Path(gt=0) ):

    if not user:
        raise HTTPException(status_code=401, detail="User authentication failed")
    
    todo_model = db.query(Todos).filter(Todos.id == todo_id)\
                  .filter(Todos.owner_id == user.get("id"))\
                  .first()
    logger.info('update todo, todo retrieved : {}'.format(todo_model))
    try:
        if todo_model is not None:
            # todo_model = Todos(**todo_request.model_dump())
            todo_model.title = todo_request.title
            todo_model.complete = todo_request.complete
            todo_model.priority = todo_request.priority
            todo_model.description = todo_request.description
            todo_model.owner_id = user.get("id")

            db.add(todo_model)
            db.commit()
           
        else:
            raise HTTPException(status_code=404, detail='Todo id is not exist')
    except Exception as e:
        raise HTTPException(status_code=400 , detail=str(e))

@router.delete('/todo/delete/{todo_id}', status_code=status.HTTP_204_NO_CONTENT)
async def delete_todo(user: user_dependency, db : db_dependency, todo_id : int = Path(gt=0)):
    if not user:
        raise HTTPException(status_code=401, detail="User authentication failed")
    
    todo_model = db.query(Todos).filter(Todos.id == todo_id)\
                  .filter(Todos.owner_id == user.get("id"))\
                  .first()
    if todo_model is not None:
        db.query(Todos).filter(Todos.id == todo_id).delete()
        db.commit()
        return {'msg': f'Deleted successfully : {todo_id}'}
    else:
        raise HTTPException(status_code=404, detail=(f'Provided todo not found :  {todo_id}'))

