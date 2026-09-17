from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.declarative import declarative_base
# SQLALCHEMY_DATABASE_URI = 'sqlite:///./todos.db'

# engine = create_engine(SQLALCHEMY_DATABASE_URI, connect_args={"check_same_thread": False})
db_url = "postgresql://postgres:admin@localhost:5432/restapi"

engine = create_engine(db_url)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()



