from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.declarative import declarative_base

import psycopg2
from psycopg2.extras import RealDictCursor #outputs as a python comma separated dicts


from config import settings

# sqlalchemy database url
    #postgresql://dbuser:password@host:port/dbname

#trying to connect to db using psycopg2 for trial
try:
    conn = psycopg2.connect(
        host="localhost",
        database="goalflow_db",
        user="goalflow_user",
        password="goalflow_password",
        cursor_factory=RealDictCursor
    )
    print("Successfully connected to database via psycopg2")
except Exception as e:
    print("Failed to connect using psycopg2")
    print("Error:", e)

#db url structure;
#dburl = postgresql://db_user:db_pw@host:port/db_name
DATABASE_URL=f'postgresql://{settings.DB_USER}:{settings.DB_PASSWORD}@{settings.DB_HOST}:{settings.DB_PORT}/{settings.DB_NAME}'
engine = create_engine(DATABASE_URL)

sessionLocal = sessionmaker(autoflush=False, autocommit=False, bind=engine)

Base = declarative_base()

def get_db():
    db = sessionLocal()
    try:
        yield db
    finally:
        db.close()