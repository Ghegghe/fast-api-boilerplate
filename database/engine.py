from sqlmodel import create_engine
from os import getenv

user = getenv("DB_USER", "myuser")
password = getenv("DB_PASSWORD", "mypassword")
host = getenv("DB_HOST", "127.0.0.1")
port = "5432"
database = getenv("DB_NAME", "fast-api-boilerplate")

connection_str = f"postgresql://{user}:{password}@{host}:{port}/{database}"

engine = create_engine(connection_str, echo=False)
