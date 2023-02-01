# https://fastapi.tiangolo.com/tutorial/sql-databases/?h=sql
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

# database location: ./sql_ap.sqlite
SQLALCHEMY_DATABASE_URL = "sqlite:///./sql_app.sqlite"

engine = create_engine(
    SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False}
)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()
