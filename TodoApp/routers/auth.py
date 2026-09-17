from datetime import timedelta, datetime, timezone
from typing import TypeAlias
from zoneinfo import ZoneInfo

from fastapi import FastAPI, HTTPException
import pytz
from starlette import status
from db_dependency.db_depends import get_db
from models import UserRequest, Token
from database_models import Users
from fastapi import APIRouter
from loggers import get_logger
from passlib.context import CryptContext
from typing import Annotated
from fastapi import Depends
from sqlalchemy.orm import Session
from fastapi.security import OAuth2PasswordRequestForm, OAuth2PasswordBearer
from jose import JWTError, jwt

router = APIRouter(prefix="/auth", tags=["auth"])

SECRET_KEY = "64acc507192d0e656b4d8a38168e9ca18a1885c5dded69d2255c6a29755f25c5"
ALGORITHM = "HS256"
bcrypt_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
oauth2_bearer = OAuth2PasswordBearer(tokenUrl="auth/token")

logger = get_logger(__name__)

db_dependency: TypeAlias = Annotated[Session, Depends(get_db)]


@router.get("/")
async def get_user():
    return {"user ": " authenticated"}


@router.post("/user/create", status_code=status.HTTP_201_CREATED)
async def create_user(db: db_dependency, new_request: UserRequest):
    logger.info("Creating a new user with username: %s", new_request.username)
    logger.info(new_request)
    try:
        create_user_model = Users(
            username=new_request.username,
            firstname=new_request.firstname,
            lastname=new_request.lastname,
            email=new_request.email,
            hashed_password=bcrypt_context.hash(new_request.password),
            is_active=new_request.is_active,
            role=new_request.role,
        )

        db.add(create_user_model)
        db.commit()

        return {"user": "created successfully"}
    except Exception as e:
        logger.error("Error creating user: %s", e)
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/token", response_model=Token)
async def login_for_access_token(
    form_date: Annotated[OAuth2PasswordRequestForm, Depends()], db: db_dependency
):
    user = authenticate_user(
        db, username=form_date.username, password=form_date.password
    )
    if not user:

        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    logger.info(f"Authenticated user: {user.__dict__}")
    token = create_access_token(
        username=user.username,
        user_id=user.id,
        role=user.role,
        expires_delta=timedelta(minutes=20),
    )
    return {"access_token": token, "token_type": "bearer"}


def authenticate_user(db: db_dependency, username: str, password: str):
    user = db.query(Users).filter(Users.username == username).first()
    # logger.info(f"Retrieved user from DB: {user.__dict__ if user else 'None'}")
    if not user:
        return False
    if not bcrypt_context.verify(password, user.hashed_password):
        return False
    return user


def create_access_token(
    username: str, user_id: int, role: str, expires_delta: timedelta
):
    encode = {"sub": username, "user_id": user_id, "role": role}
    # now_ist = datetime.now(ZoneInfo("Asia/Kolkata"))
    ist = pytz.timezone("Asia/Kolkata")
    logger.info(
        "Encoding JWT - time utc:",
        datetime.now(timezone.utc),
        "time ist:",
        datetime.now(ist),
    )
    expires = datetime.now(ist) + expires_delta
    print("Encoding JWT with payload:", encode, "with expiration:", expires)
    encode.update({"exp": expires})
    return jwt.encode(encode, SECRET_KEY, algorithm=ALGORITHM)


async def get_current_user(token: Annotated[str, Depends(oauth2_bearer)]):
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username: str = payload.get("sub")
        user_id: int = payload.get("user_id")
        user_role: str = payload.get("role")
        if username is None or user_id is None:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid authentication credentials",
                headers={"WWW-Authenticate": "Bearer"},
            )
        return {"username": username, "id": user_id, "user_role": user_role}
    except jwt.PyJWTError, JWTError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid authentication credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )
