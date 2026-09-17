from sqlalchemy import Column, ForeignKey, Integer, String, Boolean, TIMESTAMP
import pytz
from datetime import datetime

from database import Base

# Define IST timezone
ist = pytz.timezone("Asia/Kolkata")

class Todos(Base):
    __tablename__ = "todos"

    id = Column(Integer, primary_key=True, index=True,  autoincrement=True)
    title = Column(String)
    description = Column(String)
    priority = Column(Integer)
    complete = Column(Boolean, default=False)
    owner_id = Column(Integer, ForeignKey("users.user_id"), name="owner_id", nullable=False)

class Users(Base):
    __tablename__ = "users"

    id = Column(Integer, name = "user_id",primary_key=True, index=True)
    username = Column(String, name="user_name", unique=True, index=True)
    firstname = Column(String, name="first_name",nullable=False)
    lastname = Column(String, name="last_name",nullable=True)
    email = Column(String, name="email", unique=True, index=True)
    hashed_password = Column(String, name="hashed_password", nullable=False)
    created_at = Column(TIMESTAMP , name="created_date", nullable=False, default=lambda:datetime.now(ist))
    last_login = Column(String, name="last_login", nullable=True)
    is_active = Column(Boolean, name="is_active", default=True)
    role = Column(String, name="role", default="user", nullable=False)