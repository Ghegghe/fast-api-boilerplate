from sqlmodel import SQLModel, create_engine
from database import link_models
from database import models

user = "myuser"
password = "mypassword"
host = "127.0.0.1"
port = "5432"
database = "fast-api-boilerplate"

connection_str = f"postgresql://{user}:{password}@{host}:{port}/{database}"

engine = create_engine(connection_str, echo=True)

SQLModel.metadata.create_all(engine)
