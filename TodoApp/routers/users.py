from loggers import get_logger
from typing import Annotated, TypeAlias
from sqlalchemy.orm import Session
from fastapi import APIRouter, Depends, HTTPException, Path
from database import SessionLocal
from database_models import Users
from .auth import get_current_user
from starlette import status
from passlib.context import CryptContext
from models import UserVerification


router = APIRouter(
    prefix="/users",
    tags=["users"]
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
bcrypt_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

@router.get("/details", status_code=status.HTTP_200_OK)
async def get_current_user_info(current_user: user_dependency, db: db_dependency):
    logger.info(f"Current user: {current_user}")
    if not current_user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Not authenticated"
        )
    db_user = db.query(Users).filter(Users.id == current_user["id"]).first()
    if not db_user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
    db_user.hashed_password = "********"  # Hide the password before returning the user object
    return db_user
    

@router.post("/change-password", status_code=status.HTTP_200_OK)
async def change_password(current_user: user_dependency, db: db_dependency, password_change_req: UserVerification ):
    logger.info(f"Current user: {current_user}")
    if password_change_req.password == password_change_req.new_password:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="New password must be different from the current password"
        )
    if not current_user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Not authenticated"
        )
    db_user = db.query(Users).filter(Users.id == current_user["id"]).first()
    if not db_user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
    if not bcrypt_context.verify(password_change_req.password, db_user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Incorrect current password"
        )
    db_user.hashed_password = bcrypt_context.hash(password_change_req.new_password)
    db.commit()
    return {"detail": "Password changed successfully"}