# Database settings
import os
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from dotenv import load_dotenv, find_dotenv

load_dotenv(find_dotenv())

NAME = os.environ["DB_NAME"]
HOST = os.environ["DB_HOST"]
PORT = os.environ["DB_PORT"]
USER = os.environ["DB_USER"]
PASSWORD = os.environ["DB_PASSWORD"]

# Database connection url
SQLALCHEMY_DATABASE_URL = f"postgresql+psycopg2://{USER}:{PASSWORD}@{HOST}:{PORT}/{NAME}"

engine = create_engine(SQLALCHEMY_DATABASE_URL)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()

# SECRETS
SECRET_KEY = os.environ["SECRET_KEY"]
ALGORITHM = os.environ["ALGORITHM"]
ACCESS_TOKEN_EXPIRE_MINUTES = os.environ["ACCESS_TOKEN_EXPIRE_MINUTES"]

# Middleware
ALLOWED_ORIGINS = ["*"]
ALLOWED_HOSTS = ["dev.localhost.com"]

DEBUG = os.environ["DEBUG"]
